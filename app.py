#import dependencies:
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#engine setup and database reflection:
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask setup:
app = Flask(__name__)


#index - list of routes
@app.route("/")
def welcome():
    return(
        f"Welcome to the weather observation API.<br/>"
        f"Please select from the following options:<br/>"
        f"<br/>"
        f"<b/><u/>STATIC LINKS:</b></u><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"<b/><u/>DYNAMIC LINKS:</b></u> (input a date where start or end are reflected in the URL in YYYY-MM-DD format)<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

#display as jsonified dictionary the total precipitation per day for the last year's worth of data
@app.route("/api/v1.0/precipitation")
def rain():

    session = Session(engine)

    results = session.query(Measurement.date,func.sum(Measurement.prcp)).\
    filter(Measurement.date >= '2016-08-23').\
    group_by(Measurement.date).all()

    session.close()
    
    dates_rain = dict(results)

    return jsonify(dates_rain)

#display the station IDs
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
            
    session.close()

    station_names = list(np.ravel(results))

    return jsonify(station_names)

#display the temperature observations of the last year's worth of data for station USC00519281
@app.route("/api/v1.0/tobs")
def observations():
    session = Session(engine)
    temp_freq = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= '2016-08-23').\
        filter(Measurement.station == 'USC00519281').all()

    session.close()

    return jsonify(temp_freq)
        
@app.route("/api/v1.0/<start>")
def start_date_only(start):
    search_term = start
    session = Session(engine)
    results = session.query(Measurement.date, func.min(Measurement.tobs),func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
             filter(Measurement.date >= search_term).group_by(Measurement.date).all()

    session.close()
    
    return jsonify(results)          


@app.route("/api/v1.0/<start>/<end>")
def start_end_only(start, end):
    begin = start
    end = end
    session = Session(engine)
    results = session.query(Measurement.date, func.min(Measurement.tobs),func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
             filter(Measurement.date.between(begin, end)).group_by(Measurement.date).all()
    
    session.close()

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)