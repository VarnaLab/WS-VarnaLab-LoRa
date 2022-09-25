function decodeUplink(input) {

  var buf_temp = new ArrayBuffer(4);
  var view_temp = new DataView(buf_temp);
  const temp_bytes=input.bytes.slice(0,4);

  var buf_pres = new ArrayBuffer(4);
  var view_pres = new DataView(buf_pres);
  const pres_bytes=input.bytes.slice(4,8);
  
  var buf_hum = new ArrayBuffer(4);
  var view_hum = new DataView(buf_hum);
  const hum_bytes=input.bytes.slice(8,12);
  
  var buf_pm10 = new ArrayBuffer(8);
  var view_pm10 = new DataView(buf_pm10);
  const pm10_bytes=input.bytes.slice(12,20);
  
  var buf_pm25 = new ArrayBuffer(8);
  var view_pm25 = new DataView(buf_pm25);
  const pm25_bytes=input.bytes.slice(20,28);

  temp_bytes.forEach(function (b, i) {
      view_temp.setUint8(i, b);
  });
  
  pres_bytes.forEach(function (b, i) {
      view_pres.setUint8(i, b);
  });
  
  hum_bytes.forEach(function (b, i) {
      view_hum.setUint8(i, b);
  });
  
  pm10_bytes.forEach(function (b, i) {
      view_pm10.setUint8(i, b);
  });
  
  pm25_bytes.forEach(function (b, i) {
      view_pm25.setUint8(i, b);
  });
  
  //var temp = view_temp.getFloat64(0);
  var temp = view_temp.getInt32(0);
  var pres = view_pres.getInt32(0);
  var hum = view_hum.getInt32(0);
  var pm10 = view_pm10.getFloat64(0);
  var pm25 = view_pm25.getFloat64(0);
  
  //Варна е на 80м надм. височина
  const above_sea_level=80;
  
  var slp = pres + ((pres * 9.80665 * above_sea_level)/(287 * (273 + temp + (above_sea_level/400))));
  
  var p25=Math.round(pm10*10)/10;
  var p10=Math.round(pm25*10)/10;
  pm10= p10.toString();
  pm25= p25.toString();
	
  return  {
      data: {
        id: 1,
	      data:[
		          {
			          name:'bme280',
			          type:"temp_sensor",
			          data: {
				                temperature: temp,
				                actual_pressure:pres,
				                humidity:hum,
				                sea_level_pressure:Math.round(slp)
			                }
		          },
		          {
			          name:"dust",
			          type:"dust_sensor",
			          data: {
				          pm10: pm10,
				          pm25: pm25
			            }
		          }
	           ]
      
  }
 }
}