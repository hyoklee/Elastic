<?php
// $range = '60-120';
$range = '294-297';
// $range = '298-301';

// Apache httpd
// $host = "localhost";
// Apache tomcat default servlet
$host = "localhost:8889";
$socket = fsockopen($host,80);
// $packet = "GET /index.php HTTP/1.1\r\nHost: $host\r\nRange:bytes=$range\r\nAccept-Encoding: gzip\r\nConnection: close\r\n\r\n";
// $packet = "GET /MOD14CM1.201401.005.01.hdf HTTP/1.1\r\nHost: $host\r\nRange:bytes=$range\r\nAccept-Encoding: gzip\r\nConnection: close\r\n\r\n";
$packet = "GET /3B43.070901.6A.HDF HTTP/1.1\r\nHost: $host\r\nRange:bytes=$range\r\nAccept-Encoding: gzip\r\nConnection: close\r\n\r\n";
fwrite($socket,$packet);
// Read enough packets for header.
$data = fread($socket, 1024);
// print($data);
// print(strlen($data));
// Last 4 bytes are the first float value.
$str = substr($data, -4);
// print($str);
$val = unpack('f', strrev($str));
var_dump($val);
// print(1.0 + $val[1]);
?>
