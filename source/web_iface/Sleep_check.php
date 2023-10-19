<!DOCTYPE html>
<html>
<head>
<title>Config XXX Submitted</title>

<style>
    body {
        width: 35em;
        height: 100vh;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
        //background-color:green;
        background-image: linear-gradient(lightblue, darkblue);
    }
</style>
</head>
<body>
<br>
<h1>Minion XXX Launch Prep</h1>
<br>
<br>
<h3>Step 1: Reset sample counter, Final Samples Status Flag and archive previous data.</h3>
<form method='post' action=''>
<input type='submit' name='new_mission' value='Archive data and begin mission' />
</form>
<br>
<h3>Step 2: Download the Mission Configuration File</h3>
<form method='post' action=''>
<input type='submit' name='download' value='Download Minion Configuration' />
</form>
<br>
<h3>Step 3: Turn Minion off before deployment.</h3>
<form method='post' action=''>
<input type='submit' name='shutdown' value='Set Minion XXX to Sleep' />
</form>
<br>
<h3>Step 4: Once the Blue LED is no longer illuminated, attach the magnet to keep the Minion off.
If the magnet is not attached, the Minion will automatically restart after 60 seconds.</h3>
<br>
<form action="/index.php" method="post">
<input type="submit" value="Return">
</form>
<br>
<br>
</body>
</html>

<?php
if(isset($_POST['new_mission'])){
echo nl2br($output);
$command = escapeshellcmd('sudo python /var/www/html/new_mission.py');
$output = shell_exec($command);
// echo $output;
echo nl2br($output);
echo '<br>Ready to begin Mission!<br>';
}
?>

<?php
if(isset($_POST['shutdown'])){

$command = escapeshellcmd('sudo python3 /var/www/html/Minion_sleep.py');
$output = shell_exec($command);
echo "Minion returned to sleep cycle!\n";
echo "Goodbye!";
}
?>

<?php
if(isset($_POST['download'])){

$file_name = '/home/pi/Desktop/Minion_config.ini';

header('Content-Description: File Transfer');
header('Content-Type: application/octet-stream');
header('Content-Disposition: attachment; filename='.basename($file_name));
header('Content-Transfer-Encoding: binary');
header('Expires: 0');
header('Cache-Control: must-revalidate');
header('Pragma: public');
header('Content-Length: ' . filesize("/var/www/html/".$file_name));
ob_end_clean();
ob_clean();
flush();
readfile($file_name);

}
?>
