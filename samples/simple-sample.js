var epoch = new Date().getTime();

var exposures = [];

for(var i = 0; i < 450; i++){
  exposures.push({
    "name": "eight-hour-test",
    "ts": epoch + (i * 64000)
  })
}

console.log(JSON.stringify(exposures));
