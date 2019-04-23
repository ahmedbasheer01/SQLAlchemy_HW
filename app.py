import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    return (
        f"<h1>Welcome to the Climate API!</h1>"
        f"<h3>Available Routes:</h3>"
        f"<h3>/api/precipitation</h3>"
        f"<h3>/api/stations</h3>"
        f"<h3>/api/temperature</h3>"
        f"<h3>/api/'start_date'</h3>"
        f"<h3>/api/'start_date'/'end_date'</h3>"
        f"<p style='color:red;'> <b>*date format:yyyy-mm-dd</b></p>"
    )

@app.route("/api/precipitation")
def precipitation():
  
    #Query all data and prcp data
    results = session.query(Measurement.date, Measurement.prcp).all()

    all_prcp=[]

    for p_date, prcp in results:
        prcp_dict = {}
        prcp_dict[p_date] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(f"PRECIPITATION FOR THE LAST YEAR",all_prcp)

@app.route("/api/stations")
def stations():
  
    #Query all stations
    results = session.query(Station.name).all()

    return jsonify(results)


@app.route("/api/temperature")
def temperature():
    
    #Find Latest Date
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = last_date[0]

    #Deconstrut last date into yr, mo, day
    last_yr = int(last_date[0:4])
    last_mo = int(last_date[5:7])
    last_day = int(last_date[-2:])

    #Find date that is 365 days prior to last date
    query_date = str(dt.date(last_yr, last_mo, last_day) - dt.timedelta(days=366))

    # Design a query to retrieve the last 12 months of temperature data, ordered by date
    temp_data = session.query(Measurement.tobs).\
    filter(Measurement.date > query_date).\
    order_by(Measurement.date).all()

    return jsonify(f"TEMPERATURE FOR THE LAST YEAR",temp_data)


#@app.route("/api/<start_date>")
@app.route("/api/<start_date>", defaults={"end_date": "2017-08-23"})
@app.route("/api/<start_date>/", defaults={"end_date": "2017-08-23"})
@app.route("/api/<start_date>/<end_date>")
def temperature_start(start_date, end_date):

    #appropriate string for date
    start_date = start_date.replace(" ", "-")
    end_date = end_date.replace(" ", "-")

    # Design a query to retrieve from start date to last date in table
    #calc min temp, max, temp, avg temp
    low_temp= session.query(func.min(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date).first()

    high_temp= session.query(func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date).first()

    avg_temp= np.round(session.query(func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).\
            filter(Measurement.date <= end_date).first())
    
    result_temp = "Low_Temp: " + str(low_temp[0]) + \
                    ", High_Temp: " + str(high_temp[0]) + \
                        ", Avg_Temp: " + str(avg_temp[0]) 
            
    request = "Start Date: " + start_date + ", End Date: " + end_date
    return jsonify(request, result_temp)

if __name__ == "__main__":
        app.run(debug=True)
