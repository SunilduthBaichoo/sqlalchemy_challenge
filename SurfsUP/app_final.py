# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB

session = Session(engine)
#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available API routes."""
    return (
        f"Welcome to the Climate API."
        f"Copy and paste the respective path to complete the URL"
        f" Date format : yyyy-mm-dd <br/>"
        f"/api/v1.0/precipitation <br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
        
    )

# Route for precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Retrieve the last 12 months of precipitation data """ 

    # Starting from the most recent data point in the database. 
    most_recent_date = session.query(func.max(measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')

    # Calculate the date one year from the last date in data set.
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = (
        session.query(measurement.date, measurement.prcp)
        .filter(measurement.date >= one_year_ago)
        .all()
        )

    # Convert the query results to a dictionary with date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    """ Close session"""
    session.close()

    
    return jsonify(precipitation_dict)

# Route for station data

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Query to get all unique station IDs"""
    stations = session.query(station.station).distinct().all()

    # Convert the result to a list of station IDs
    station_list = [station[0] for station in stations]

    """ Close session"""
    session.close()


    return jsonify(station_list)

# Route for temperature observations for the last year

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Get the most active station
    most_active_station = (
            session.query(measurement.station)
            .group_by(measurement.station)
            .order_by(func.count(measurement.station).desc())
            .first())[0]  
    
    # Using the most active station id
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram

    most_recent_date = session.query(func.max(measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')

    # Calculate the date one year from the last date in data set.
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    # Perform a query to retrieve the data and temperature scores
    temperature_data = (
            session.query( measurement.tobs)
             .filter(measurement.station == most_active_station) 
             .filter(measurement.date >= one_year_ago)
             .all()
            )

    # Convert the query result into a list of temperatures
    temperatures = [temp[0] for temp in temperature_data]

    """ Close session"""
    session.close()


    return jsonify(temperatures)


# Route for temperature statistics from a given start date
@app.route("/api/v1.0/<start>")
def stats_from_start(start):
    # Convert start date to a datetime object
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")

     # Create our session (link) from Python to the DB
    session = Session(engine)


    # Query for TMIN, TAVG, TMAX from the start date onward
    results = session.query(
        func.min(measurement.tobs).label("TMIN"),
        func.avg(measurement.tobs).label("TAVG"),
        func.max(measurement.tobs).label("TMAX")
    ).filter(measurement.date >= start_date).all()

    
    # Convert results to a dictionary
    stats = {
        "TMIN": results[0].TMIN,
        "TAVG": results[0].TAVG,
        "TMAX": results[0].TMAX
    }

    """ Close session"""
    session.close()

    return jsonify(stats)

# Route for temperature statistics between a start and end date
@app.route("/api/v1.0/<start>/<end>")
def stats_from_start_end(start, end):
    # Convert start and end dates to datetime objects
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")

     # Create our session (link) from Python to the DB
    session = Session(engine)


    # Query for TMIN, TAVG, TMAX between start and end dates
    results = session.query(
        func.min(measurement.tobs).label("TMIN"),
        func.avg(measurement.tobs).label("TAVG"),
        func.max(measurement.tobs).label("TMAX")
    ).filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

    # Convert results to a dictionary
    stats = {
        "TMIN": results[0].TMIN,
        "TAVG": results[0].TAVG,
        "TMAX": results[0].TMAX
    }

    """ Close session"""
    session.close()

    return jsonify(stats)


if __name__ == "__main__":
    app.run(debug=True)
