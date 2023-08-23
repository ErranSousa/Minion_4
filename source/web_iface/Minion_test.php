<!DOCTYPE html>
<html>
<head>
<title>Minion XXX Testing</title>

<style>
    h1 {text-align: center;}
    body {
        width: 35em;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
        background-color:lightskyblue;
    }
</style>
</head>
<body>

<h1> Test sampling functions on Minion XXX! </h1>
<br>
<fieldset>
<h3> Image Test</h3>
<br>
<form method='post' action=''>
<input type='submit' name='capture' value='Capture!' />
<input type='submit' name='download' value='Capture & Download!' />
</form>
</fieldset>
<fieldset>
<h3> Pressure Sensor Test</h3>
<br>
<form method='post' action=''>
<input type='submit' name='pressure' value='PRESSURE' />
</form>
<br>

<?php
if(isset($_POST['pressure'])){

$command = escapeshellcmd('sudo python3 /home/pi/Documents/Minion_scripts/Pressure_test.py');
$output_pres = shell_exec($command);
echo "Pressure reading: " . $output_pres . " dbar";

}
?>
<br>
</fieldset>
<fieldset>
<h3> Temperature Sensor Test</h3>
<br>
<form method='post' action=''>
<input type='submit' name='temperature' value='TEMPERATURE' />
</form>
<br>
<?php
if(isset($_POST['temperature'])){

$command = escapeshellcmd('sudo python3 /home/pi/Documents/Minion_scripts/Temperature_test.py');
$output_temp = shell_exec($command);
echo "Temperature reading: " . $output_temp . " C";

}
?>
<br>
</fieldset>
<fieldset>
<h3> Burn Wire Test</h3>
<br>
<form method='post' action=''>
<input type='submit' name='BURN' value='BURN WIRE' />
</form>
<br>
<?php
if(isset($_POST['BURN'])){

$command = escapeshellcmd('sudo python3 /var/www/html/test_burnwire.py');
//$output_BURN = shell_exec($command);
// echo $output_BURN;
// echo '<pre>';
// passthru($command);
// echo '</pre>';
header('X-Accel-Buffering: no');
while (@ ob_end_flush()); // end all output buffers if any

$proc = popen($command, 'r');
echo '<pre>';
while (!feof($proc))
{
    echo fread($proc, 4096);
    @ flush();
}
echo '</pre>';
}
?>
<br>
</fieldset>
<fieldset>
<h3> LED Ring Test</h3>
<br>
<form method='post' action=''>
<input type='submit' name='LED_RING' value='LED Ring' />
</form>
<br>
<?php
if(isset($_POST['LED_RING'])){

$command = escapeshellcmd('sudo python3 /var/www/html/test_LED_Ring.py');
header('X-Accel-Buffering: no');
while (@ ob_end_flush()); // end all output buffers if any
$proc = popen($command, 'r');
echo '<pre>';
while (!feof($proc))
{
    echo fread($proc, 4096);
    @ flush();
}
echo '</pre>';
}
?>
<br>
</fieldset>

<fieldset>
<h3> Recovery Strobe Test</h3>
<br>
<form method='post' action=''>
<input type='submit' name='STROBE' value='Recovery Strobe' />
</form>
<br>
<?php
if(isset($_POST['STROBE'])){

$command = escapeshellcmd('sudo python3 /var/www/html/test_recovery_strobe.py');
header('X-Accel-Buffering: no');
while (@ ob_end_flush()); // end all output buffers if any
$proc = popen($command, 'r');
echo '<pre>';
while (!feof($proc))
{
    echo fread($proc, 4096);
    @ flush();
}
echo '</pre>';
}
?>
<br>
</fieldset>

<br>
<form action="/index.php" method="post">
<input type="submit" value="Return">
</form>
</body>
</html>
<br>
<br>
<br>
<br>
<?php
if(isset($_POST['download'])){

$command = escapeshellcmd('sudo python3 /var/www/html/Image_test.py');
$output = shell_exec($command);

$file = '/home/pi/testimage.jpg';
$type = 'image/jpeg';
header('Content-Disposition: attachment; filename='.basename($file));
header('Content-Description: File Transfer');
header('Content-Type:'.$type);
header('Content-Transfer-Encoding: binary');
header('Expires: 0');
header('Cache-Control: must-revalidate');
header('Pragma: public');
header('Content-Length: ' . filesize($file));
ob_clean();
flush();
readfile($file);



}
?>

<?php
if(isset($_POST['capture'])){

$command = escapeshellcmd('sudo python3 /var/www/html/Image_test.py');
$output = shell_exec($command);
echo $output;

$file = '/home/pi/testimage.jpg';
$type = 'image/jpeg';
header('Content-Type:'.$type);
header('Content-Length: ' . filesize($file));
ob_clean();
flush();
readfile($file);

}
?>

