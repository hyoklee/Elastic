<?php
// HDF5 - OCO-2 1086 bytes of gzipped chunk.
$range = '108875990-108877075';

// Apache httpd
$host = "localhost";
$socket = fsockopen($host,80);
$packet = "GET /oco2_L2StdND_03945a_150330_B6000_150331024816.h5 HTTP/1.1\r\nHost: $host\r\nRange:bytes=$range\r\nAccept-Encoding: gzip\r\nConnection: close\r\n\r\n";
fwrite($socket,$packet);
// Read enough packets for header.
$data_gz = fread($socket, 2048);
// print(substr($data_gz, -1086));
$data = gzuncompress(substr($data_gz, -1086));
// print($data);

// HDF5 1 byte.
$str = substr($data, 0, 1);
print($str);
$val = unpack('c', $str);
var_dump($val);
?>
