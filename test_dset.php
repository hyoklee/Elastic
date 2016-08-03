<?php

$range = '294-2304293';
$host = "localhost";
$socket = fsockopen($host,80);
$packet = "GET /3B43.070901.6A.HDF HTTP/1.1\r\nHost: $host\r\nRange:bytes=$range\r\nAccept-Encoding: gzip\r\nConnection: close\r\n\r\n";
fwrite($socket,$packet);
// Read enough packets for header.
$alldata = '';
while (!feof($socket)){
  $alldata .= fread($socket, 8192);
}
fclose($socket);
// Uncomment the following to print out values.
/*
 $data = substr($alldata, -2304000);
 for ($i=0; $i < 2304000; $i=$i+4) {
   $str = substr($data, $i, 4);
   $val = unpack('f', strrev($str));
    var_dump($val);
}
*/

?>
