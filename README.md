# toggl-task-track
Keep track of time that a set of lights are turned on by querying my home automation system (Universal Devices ISY). Record time in  toggl track. 

This python script detects the change of status of "lights on" or "lights off" in my workshop.   When lights are turned on, a time tracker in my toggl.com account is initiated.  When lights are turned off, the current time tracker at toggl is stopped. 

The script reads status from my Universal Devices  [ISY994 home automation controller](https://www.universal-devices.com/product/isy994-pro-oadr/).  The script then starts or stops a Toggl time tracker through the [Toggl API v9](https://developers.track.toggl.com/docs/api/me/index.html)

## My Use Case

I'm  a somewhat retired guy who restores pianos in my home workshop.  Despite being somewhat retired, I want to track time spent in the shop to keep myself disciplined to work regularly at productive and creative tasks.  This app, which is triggered by cron every minute, will log time at Toggl and serve as a proxy for my "time card".  It works well for me, because I'm reliable at turning the lights on and off upon entering and exiting the shop.   I've proven to be much less reliable at starting and stopping a Toggl task working in the shop. 
