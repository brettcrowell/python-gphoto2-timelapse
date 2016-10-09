var epoch = new Date().getTime();

var exposures = [];

// 24 hour timelapse = (24*60*60) / (60*30)
// ie: (24h * 60m * 60s) / (60s * 30fps)

for(var i = 0; i < 1800; i++){
  exposures.push({
    "name": "eight-hour-test",
    "ts": epoch + (i * 48000)
  })
}

console.log(JSON.stringify(exposures));
