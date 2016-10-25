var epoch = new Date().getTime();

var exposures = [];

// 24 hour timelapse = (24*60*60) / (60*30)
// ie: (24h * 60m * 60s) / (60s * 30fps)

var delaySeconds = 30;
var inputHours = 24;
var outputSeconds = 60;
var outputFps = 30;

var intervalSeconds = (inputHours * 60 * 60) / (outputSeconds * outputFps);
var numFrames = outputSeconds * outputFps;

for(var i = 0; i < numFrames; i++){
  exposures.push({
    "name": "twenty-four-hour-test",
    "ts": (delaySeconds * 1000) + epoch + (i * (intervalSeconds * 1000))
  })
}

console.log(JSON.stringify(exposures));
