<!DOCTYPE html>
<html>
<head>
<title>Minion XXX GPS & Iridium Tests</title>

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

<h1> Test the GPS and Iridium Modem on Minion XXX! </h1>

<fieldset>
<h3> GPS Module Test</h3>
<br>
<form method='post' action=''>
<input type='submit' name='GPS' value='Acquire GPS Position' />
</form>
<br>
<?php
if(isset($_POST['GPS'])){

$command = escapeshellcmd('sudo python3 /home/pi/Documents/Minion_tools/gps_test.py');
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
<h3> Iridium Modem Test</h3>
<br>
<form method='post' action=''>
<input type='submit' name='Iridium' value='Transmit Iridium Message' />
</form>
<br>
<?php
if(isset($_POST['Iridium'])){

$command = escapeshellcmd('sudo python /home/pi/Documents/Minion_tools/Iridium_test.py');
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
<input type="submit" value="Home">
</form>

</body>
</html>
