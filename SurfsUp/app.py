from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Use automap_base() to prepare the classes
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# Helper Functions
def get_date_one_year_ago():
    """Returns the date one year ago from the most recent date in the dataset."""
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date, '%Y-%m-%d')
    return most_recent_date - timedelta(days=365)

def query_temp_stats(start_date, end_date=None):
    """Returns the min, avg, and max temperatures for the specified date range."""
    query = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start_date)
    
    if end_date:
        query = query.filter(Measurement.date <= end_date)
    
    results = query.all()
    min_temp, avg_temp, max_temp = results[0]
    return {'TMIN': min_temp, 'TAVG': avg_temp, 'TMAX': max_temp}

app = Flask(__name__)

# Routes
@app.route('/')
def home():
    return (
        "Welcome to the Climate API!<br>"
        "Available Routes:<br>"
        "/api/v1.0/precipitation<br>"
        "/api/v1.0/stations<br>"
        "/api/v1.0/tobs<br>"
        "/api/v1.0/<start><br>"
        "/api/v1.0/<start>/<end><br>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    one_year_ago = get_date_one_year_ago()
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

@app.route('/api/v1.0/stations')
def stations():
    results = session.query(Station.station, Station.name).all()
    stations_list = [{'station': station, 'name': name} for station, name in results]
    return jsonify(stations_list)

@app.route('/api/v1.0/tobs')
def tobs():
    one_year_ago = get_date_one_year_ago()
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count().desc()).first()[0]
    
    results = session.query(Measurement.tobs).filter(
        Measurement.station == most_active_station,
        Measurement.date >= one_year_ago
    ).all()
    
    tobs_list = [tobs for tobs, in results]
    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>')
def start(start):
    stats = query_temp_stats(start)
    return jsonify(stats)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start, end):
    stats = query_temp_stats(start, end)
    return jsonify(stats)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)