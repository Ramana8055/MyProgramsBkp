#Check all min and max values
from random import uniform,randint,SystemRandom
from string import ascii_uppercase,ascii_lowercase,digits


def getrandfloat(minimum,maximum):
        return str(uniform(float(minimum),float(maximum)))
def getrandint(minimum,maximum):
        return str(randint(int(minimum),int(maximum)))
def getrandstring():
	return ''.join(SystemRandom().choice(ascii_uppercase +\
			 digits +ascii_lowercase) for _ in range(50))


pathPoint_tags=[
		{"deltaLatitude":{"dtype":"value",
				  "mini":"-13107.1",
				  "maxi":"13107.1",
				  "belowmin":getrandfloat,
				  "abovemax":getrandfloat,
			          "random":getrandfloat,
				  "unavailable":" "}
		},
		{"deltaLongitude":{"dtype":"value",
				   "mini":"-13107.1",
				   "maxi":"13107.1",
				   "belowmin":getrandfloat,
				   "abovemax":getrandfloat,
			           "random":getrandfloat,
				   "unavailable":" "}
		},
		{"deltaAltitude":{"dtype":"value",
				  "mini":"1",
				  "maxi":"127.99",
				  "belowmin":getrandfloat,
				  "abovemax":getrandfloat,
			          "random":getrandfloat,
				  "unavailable":" "}
		},
		{"deltaTime":{"dtype":"value",
			      "mini":"1",
			      "maxi":"655.35",
			      "belowmin":getrandfloat,
			      "abovemax":getrandfloat,
			      "random":getrandfloat,
			      "unavailable":" "}
		}
]
trace_tags=[
	    {"pathPoint":{"dtype":"structure",
			  "taglist":pathPoint_tags,
			  "repeat":"no"},
	    }
]
tracesList_tags=[
		{"trace":{"dtype":"structure",
         	          "taglist":trace_tags,
			  "repeat":"yes",
			  "repeatcount":40}
		}
]
eventHeading_tags=[
		   {"headingValue":{"dtype":"value",
				    "mini":"0",
				    "maxi":"360.0",
				    "belowmin":getrandfloat,
				    "abovemax":getrandfloat,
				    "random":getrandfloat,
				    "unavailable":" "} #Check
		   },
		   {"headingConfidence":{"dtype":"value",
					 "mini":"0",
					 "maxi":"12.6",
					 "belowmin":getrandfloat,
					 "abovemax":getrandfloat,
				         "random":getrandfloat,
					 "unavailable":" "}
		   }
]
eventSpeed_tags=[
		{"speedValue":{"dtype":"value",
			       "mini":"0",
			       "maxi":"163.82",
			       "belowmin":getrandfloat,
			       "abovemax":getrandfloat,
			       "random":getrandfloat,
			       "unavailable":" "} #Check
		},
		{"speedConfidence":{"dtype":"value",
				    "mini":"0",
				    "maxi":"12.6",
				    "belowmin":getrandfloat,
				    "abovemax":getrandfloat,
				    "random":getrandfloat,
				    "unavailable":" "}
		}
]
locationContainer_tags=[
			{"eventSpeed":{"dtype":"structure",
				       "taglist":eventSpeed_tags,
				       "repeat":"no",}
			},
			{"eventHeading":{"dtype":"structure",
					 "taglist":eventHeading_tags,
					 "repeat":"no"}
			},
			{"tracesList":{"dtype":"structure",
				       "taglist":tracesList_tags,
				       "repeat":"yes",
				       "repeatcount":7} #Max traces: 7. Can be randomized using random function
			},
			{"roadType":{"dtype":"value",
				     "mini":"0",
			             "maxi":"3",
				     "belowmin":getrandint,
				     "abovemax":getrandint,
				     "random":getrandint,
				     "unavailable":" "}
			}
]
eventPosition_tags=[ #Check the min and max
		    {"deltaLatitude":{"dtype":"value",
				      "mini":"-13107.1",
				      "maxi":"13107.1",
				      "belowmin":getrandfloat,
				      "abovemax":getrandfloat,
				      "random":getrandfloat,
				      "unavailable":" "}
		    },
		    {"deltaLongitude":{"dtype":"value",
				       "mini":"-13107.1",
				       "maxi":"13107.1",
				       "belowmin":getrandfloat,
				       "abovemax":getrandfloat,
				       "random":getrandfloat,
				       "unavailable":" "}
		    },
		    {"deltaAltitude":{"dtype":"value",
				      "mini":"1",
				      "maxi":"127.99",
				      "belowmin":getrandfloat,
				      "abovemax":getrandfloat,
				      "random":getrandfloat,
				      "unavailable":" "}
		    }
]
eventHistory_tags=[
		   {"eventPosition":{"dtype":"structure",
				     "taglist":eventPosition_tags,
				     "repeat":"no"}
		   },
		   {"pathDeltaTime":{"dtype":"value",
				     "mini":"1",
				     "maxi":"655.35",
				     "belowmin":getrandfloat,
				     "abovemax":getrandfloat,
				     "random":getrandfloat,
				     "unavailable":" "} #Check
		   },
		   {"informationQuality":{"dtype":"value",
					  "mini":"0",
					  "maxi":"7",
					  "belowmin":getrandint,
					  "abovemax":getrandint,
				          "random":getrandint,
					  "unavailable":" "} #Check
		   }
]
eventHistoryList_tags=[
			{"eventHistory":{"dtype":"structure",
					 "taglist":eventHistory_tags,
					 "repeat":"no"}
			}
]
linkedCause_tags=[
		  {"causeCodeType":{"dtype":"value",
                                    "mini":"0",
                                    "maxi":"255",
				    "belowmin":getrandint,
				    "abovemax":getrandint,
			            "random":getrandint,
				    "unavailable":" "}
                  },
                  {"subCauseCodeType":{"dtype":"value",
                                       "mini":"0",
                                       "maxi":"255",
				       "belowmin":getrandint,
				       "abovemax":getrandint,
				       "random":getrandint,
				       "unavailable":" "}
                  }
]
causeCode_tags=[
		{"causeCodeType":{"dtype":"value",
				  "mini":"0",
				  "maxi":"255",
				  "belowmin":getrandint,
				  "abovemax":getrandint,
			          "random":getrandint,
				  "unavailable":" "}
		},
		{"subCauseCodeType":{"dtype":"value",
				     "mini":"0",
				     "maxi":"255",
				     "belowmin":getrandint,
				     "abovemax":getrandint,
				     "random":getrandint,
				     "unavailable":" "}
		}
]
situationContainer_tags=[
			{"informationQuality":{"dtype":"value",
					       "mini":"1",
					       "maxi":"7",
					       "belowmin":getrandint,
					       "abovemax":getrandint,
					       "random":getrandint,
					       "unavailable":" "}
			},
			{"causeCode":{"dtype":"structure",
				      "taglist":causeCode_tags,
				      "repeat":"no"}
			},
			{"linkedCause":{"dtype":"structure",
					"taglist":linkedCause_tags,
					"repeat":"no"}
			},
			{"eventHistoryList":{"dtype":"structure",
					     "taglist":eventHistoryList_tags,
					     "repeat":"no"}
			}
]
eventPosition_tags=[
                     {"latitude":{"dtype":"value",
                                  "mini":"-90.0000000",
                                  "maxi":"90.0000000",
				  "belowmin":getrandfloat,
				  "abovemax":getrandfloat,
			          "random":getrandfloat,
				  "unavailable":" "}
                     },
                     {"longitude":{"dtype":"value",
                                   "mini":"-180.0000000",
                                   "maxi":"180.0000000",
				   "belowmin":getrandfloat,
				   "abovemax":getrandfloat,
				   "random":getrandfloat,
				   "unavailable":" "},
                     },
                     {"semiMajorAxis":{"dtype":"value",
                                       "mini":"0",       #CHECK
                                       "maxi":"4094",
				       "belowmin":getrandint,
				       "abovemax":getrandint,
				       "random":getrandint,
				       "unavailable":" "}      #CHECK
                     },
                     {"semiMinorAxis":{"dtype":"value",
                                       "mini":"0",       #CHECK
                                       "maxi":"4094",
				       "belowmin":getrandint,
				       "abovemax":getrandint,
				       "random":getrandint,
				       "unavailable":" "}
                     },
                     {"semiMajorOrientation":{"dtype":"value",
                                              "mini":"0",
                                              "maxi":"360.0",
					      "belowmin":getrandfloat,
					      "abovemax":getrandfloat,
					      "random":getrandfloat,
					      "unavailable":" "} #CHECK
		     },
                     {"altitudeValue":{"dtype":"value",
                                       "mini":"-1000.00",
                                       "maxi":"8000.00",
				       "belowmin":getrandfloat,
				       "abovemax":getrandfloat,
				       "random":getrandfloat,
				       "unavailable":" "}    #CHECK
                     },
                     {"altitudeConfidence":{"dtype":"value",
                                            "mini":"0",
                                            "maxi":"14",
					    "belowmin":getrandint,
					    "abovemax":getrandint,
					    "random":getrandint,
					    "unavailable":" "}
                     }
]
actionID_tags=[
		{"stationID":{"dtype":"value",
                              "mini":"0",
                              "maxi":"4294967295",
			      "belowmin":getrandint,
			      "abovemax":getrandint,
			      "random":getrandint,
			      "unavailable":" "}
                },
                {"sequenceNumber":{"dtype":"value",
                                   "mini":"0",
                                   "maxi":"65535",
				   "belowmin":getrandint,
				   "abovemax":getrandint,
				   "random":getrandint,
				   "unavailable":" "}         #CHECK
		}
]
mobileContainer_tags=[
                       {"actionID":{"dtype":"structure",
				    "taglist":actionID_tags,
				    "repeat":"no"}
                       },
                       {"detectionTime":{"dtype":"string",
                                         "String":getrandstring}
                       },
 		       {"referenceTime":{"dtype":"string",
                                         "String":getrandstring}
		       },
                       {"termination":{"dtype":"choice",
                                       "first":"Cancellation"}
                       },
                       {"eventPosition":{"dtype":"structure",
                                         "taglist":eventPosition_tags,
					 "repeat":"no"}      
		       },
                       {"relevanceDistance":{"dtype":"value",
                                             "mini":"0",
                                             "maxi":"7",
					     "belowmin":getrandint,
					     "abovemax":getrandint,
					     "random":getrandint,
					     "unavailable": " "}
                       },
		       {"relevanceTrafficDirection":{"dtype":"value",
                                                     "mini":"0",
                                                     "maxi":"3",
						     "belowmin":getrandint,
						     "abovemax":getrandint,
						     "random":getrandint,
						     "unavailable":" "}
		       },
                       {"validityDuration":{"dtype":"value",
                                            "mini":"1",
                                            "maxi":"86400",
					    "belowmin":getrandint,
					    "abovemax":getrandint,
					    "random":getrandint,
					    "unavailable":" "}
                       },
                       {"transmissionInterval":{"dtype":"value",
                                                "mini":"1",
                                                "maxi":"10000",
						"belowmin":getrandint,
						"abovemax":getrandint,
						"random":getrandint,
						"unavailable":" "}
                       },
                       {"stationType":{"dtype":"value",
                                       "mini":"1",
                                       "maxi":"255",
				       "belowmin":getrandint,
				       "abovemax":getrandint,
				       "random":getrandint,
				       "unavailable":" "} #CHECK
		       }
]
denmData_tags=[
		{"mobileContainer":{"dtype":"structure",
                                    "taglist":mobileContainer_tags,
				    "repeat":"no"}
                },
                {"situationContainer":{"dtype":"structure",
                                       "taglist":situationContainer_tags,
				       "repeat":"no"}
                },
		{"locationContainer":{"dtype":"structure",
                    		      "taglist":locationContainer_tags,
				      "repeat":"no"}
		}
]
itsPdu_tags=[
	     {"protocolVersion":{"dtype":"value",
                                 "mini":"0",
                                 "maxi":"1",
				 "belowmin":getrandint,
				 "abovemax":getrandint,
				 "random":getrandint,
				 "unavailable":" "} # Not required
             },
             {"stationID":{"dtype":"value",
                           "mini":"0",
                           "maxi":"4294967295",
			   "belowmin":getrandint,
			   "abovemax":getrandint,
			   "random":getrandint,
			   "unavailable":" "}
             }
]
circular_tags=[
		{"radius":{"dtype":"value",
			   "mini":"1",
			   "maxi":"65535",
			   "belowmin":getrandint,
			   "abovemax":getrandint,
			   "random":getrandint,
			   "unavailable":" "}
		}
]
rectangular_tags=[
		   {"distance_a":{"dtype":"value",
				  "mini":"1",
				  "maxi":"65535",
				  "belowmin":getrandint,
				  "abovemax":getrandint,
				  "random":getrandint,
				  "unavailable":" "}
		   },
		   {"distance_b":{"dtype":"value",
				  "mini":"1",
				  "maxi":"65535",
				  "belowmin":getrandint,
				  "abovemax":getrandint,
				  "random":getrandint,
				  "unavailable":" "}
		  }
]
ellipsoidal_tags=[
		   {"distance_a":{"dtype":"value",
				  "mini":"1",
				  "maxi":"65535",
				  "belowmin":getrandint,
				  "abovemax":getrandint,
				  "random":getrandint,
				  "unavailable":" "}
		   },
		   {"distance_b":{"dtype":"value",
				  "mini":"1",
				  "maxi":"65535",
				  "belowmin":getrandint,
				  "abovemax":getrandint,
				  "random":getrandint,
				  "unavailable":" "}
		  }
]
denmDestinationArea_tags=[
                           {"lat":{"dtype":"value",
				   "mini":"-90.0000000",
				   "maxi":"90.0000000",
				   "belowmin":getrandfloat,
				   "abovemax":getrandfloat,
				   "random":getrandfloat,
				   "unavailable":" "}
                           },
			   {"long":{"dtype":"value",
				    "mini":"-180.0000000",
				    "maxi":"180.0000000",
				    "belowmin":getrandfloat,
				    "abovemax":getrandfloat,
				    "random":getrandfloat,
				    "unavailable":" "}
                           },
                           {"areaType":{"dtype":"AreaType",
                                        "Circular":circular_tags,
					"Rectangular":rectangular_tags,
					"Ellipsoidal":ellipsoidal_tags}
			   },
                           {"angle":{"dtype":"value",
                                     "mini":"0",
                                     "maxi":"360.0",
				     "belowmin":getrandfloat,
				     "abovemax":getrandfloat,
				     "random":getrandfloat,
				     "unavailable":" "}
                           }
]
xml_tags=[
           {"maxPacketLifeTime":{ "dtype":"value",
	                          "mini" : "0",
                                  "maxi" : "60",
				  "belowmin":getrandint,
				  "abovemax":getrandint,
				  "random":getrandint,
				  "unavailable":" "} #Not required 
	   },
           {"denmRepetitionInterval":{ "dtype":"value",
                                       "mini" :"0",
		                       "maxi" :"1000",
				       "belowmin":getrandint,
				       "abovemax":getrandint,
				       "random":getrandint,
				       "unavailable":" "}
	   },
	   {"denmRepeatDuration":{ "dtype":"value",
		                   "mini":"0",
				   "maxi":"10",
				   "belowmin":getrandint,
				   "abovemax":getrandint,
				   "random":getrandint,
				   "unavailable":" "}
           },
	   {"denmPacketMaxHopLimit":{ "dtype":"value",
                                      "mini":"0",
                                      "maxi":"10",
				      "belowmin":getrandint,
				      "abovemax":getrandint,
				      "random":getrandint,
				      "unavailable":" "}
           },
	   {"denmDestinationArea":{ "dtype":"structure",
                                    "taglist":denmDestinationArea_tags,
				    "repeat":"no"}
           },
	   {"itsPdu":{ "dtype":"structure",
                       "taglist":itsPdu_tags,
		       "repeat":"no"}
           },
	   {"denmData":{ "dtype":"structure",
                         "taglist":denmData_tags,
			 "repeat":"no"}
           }
]
