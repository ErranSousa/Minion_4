<!DOCTYPE html>
<html>
<head>
<title>Submit XXX Config</title>

<style>
    body {
        width: 35em;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
        background-color:lightskyblue;
    }
</style>
</head>
<body>
<h1>Minion <?php echo $_POST["MNumber"]; ?>!</h1>
<fieldset>
MAX Depth: <?php echo $_POST["DMAX"]; ?><br>
Ignore_WIFI-hours: <?php echo $_POST["IG_WIFI-hours"]; ?><br>
</fieldset>
<fieldset>
<legend>Sensors:</legend>
Image: <?php if ($_POST["Image"]=="Image"){echo "True";}else{echo "False";} ?><br>
BR 30 Bar Pressure Sensor: <?php if ($_POST["30Bar_Pres"]=="30Bar_Pres"){echo "True";}else{echo "False";} ?><br>
BR 100 Bar Pressure Sensor: <?php if ($_POST["100Bar_Pres"]=="100Bar_Pres"){echo "True";}else{echo "False";} ?><br>
BR Temperature Sensor: <?php if ($_POST["Temp"]=="Temp"){echo "True";}else{echo "False";} ?><br>
Oxybase O2 Sensor: <?php if ($_POST["OXY"]=="OXY"){echo "True";}else{echo "False";} ?><br>
</fieldset>
<fieldset>
<legend>Initial Sampling Mode:</legend>
Initial Sample Time (hours): <?php echo $_POST["IHours"]; ?><br>
Camera Sample Rate (minutes): <?php echo $_POST["ICamFS"]; ?><br>
Temperature and Pressure Sample Period (seconds): <?php echo $_POST["ITPFS"]; ?><br>
Dissolved Oxygen Sample Period (seconds): <?php echo $_POST["IOXYFS"]; ?><br>
</fieldset>

<fieldset>
<legend>Time Lapse Sampling Mode:</legend>
Hours: <?php echo $_POST["THours"]; ?><br>
Sample Burst Duration (min): <?php echo $_POST["DS_Time"]; ?><br>
Sample Burst Interval (min): <?php echo $_POST["DS_Interval"]; ?><br>
Camera Sample Rate (minutes): <?php echo $_POST["TCamFS"]; ?><br>
Temperature and Pressure Sample Period (seconds): <?php echo $_POST["SensorFS"]; ?><br>
Oxybase Sample Period (seconds): <?php echo $_POST["OxygenFS"]; ?><br>
</fieldset>

<fieldset>
<legend>Final Sampling Mode:</legend>
Final Sample Time (hours): <?php echo $_POST["FHours"]; ?><br>
Camera Sample Rate (minutes): <?php echo $_POST["FCamFS"]; ?><br>
Temperature and Pressure Sample Period (seconds): <?php echo $_POST["FTPFS"]; ?><br>
Dissolved Oxygen Sample Period (seconds): <?php echo $_POST["FOXYFS"]; ?><br>
</fieldset>

<fieldset>
<legend>GPS Transmission Window Settings:</legend>
GPS Transmission Window Duration (hours): <?php echo $_POST["gps_dur_hrs"]; ?><br>
GPS Position Interval (minutes): <?php echo $_POST["gps_interval_min"]; ?><br>
</fieldset>

<?php
$myfile = fopen("newconfig.txt", "w") or die("Unable to open file!");

$header = "#This is the Minion config file.\n\n";
fwrite($myfile, $header);

$Minion = "[MINION]\n"
  ."number = ".$_POST["MNumber"]."\n\n";

fwrite($myfile, $Minion);

$Mission = "[Mission]\n"
  ."abort = 0"."\n"
  ."max_depth = ".$_POST["DMAX"]."\n"
  ."ignore_wifi-hours = ".$_POST["IG_WIFI-hours"]."\n\n";
fwrite($myfile, $Mission);

$Initial_Samples = "[Initial_Samples]\n"
  ."hours = ".$_POST["IHours"]."\n"
  ."camera_sample_period = ".$_POST["ICamFS"]."\n"
  ."temppres_sample_period = ".$_POST["ITPFS"]."\n"
  ."oxygen_sample_period = ".$_POST["IOXYFS"]."\n\n";

fwrite($myfile, $Initial_Samples);

$Data_Sample = "[Time_Lapse_Samples]\n"
  ."hours = ".$_POST["THours"]."\n"
  ."sample_burst_duration = ".$_POST["DS_Time"]."\n"
  ."sample_interval_minutes = ".$_POST["DS_Interval"]."\n"
  ."camera_sample_period = ".$_POST["TCamFS"]."\n"
  ."temppres_sample_period = ".$_POST["SensorFS"]."\n"
  ."oxygen_sample_period = ".$_POST["OxygenFS"]."\n\n";

fwrite($myfile, $Data_Sample);

$Final_Samples = "[Final_Samples]\n"
  ."hours = ".$_POST["FHours"]."\n"
  ."camera_sample_period = ".$_POST["FCamFS"]."\n"
  ."temppres_sample_period = ".$_POST["FTPFS"]."\n"
  ."oxygen_sample_period = ".$_POST["FOXYFS"]."\n\n";

fwrite($myfile, $Final_Samples);

$GPS_Schedule = "[GPS]\n"
  ."gps_transmission_window = ".$_POST["gps_dur_hrs"]."\n"
  ."gps_transmission_interval = ".$_POST["gps_interval_min"]."\n\n";

fwrite($myfile, $GPS_Schedule);

if ($_POST["Image"]=="Image"){$bImage = "True";}else{$bImage = "False";}
if ($_POST["30Bar_Pres"]=="30Bar_Pres"){$b30bar = "True";}else{$b30bar = "False";}
if ($_POST["100Bar_Pres"]=="100Bar_Pres"){$b100bar = "True";}else{$b100bar = "False";}
if ($_POST["Temp"]=="Temp"){$btemp = "True";}else{$btemp = "False";}
if ($_POST["OXY"]=="OXY"){$boxy = "True";}else{$boxy = "False";}

$Sampling_scripts = "[Sampling_scripts]\n"
  ."image = ".$bImage."\n"
  ."30Ba-pres = ".$b30bar."\n"
  ."100Ba-pres = ".$b100bar."\n"
  ."temperature = ".$btemp."\n"
  ."oxybase = ".$boxy."\n\n";

fwrite($myfile, $Sampling_scripts);

fclose($myfile);
?>

<h2>Config XXX saved!</h2>

<form action="/form_submitted.php" method="post">
<input type="submit" value="Write Minion Config!">
</form>

<br>
<form action="/index.php" method="post">
<input type="submit" value="Return">
</form>

</body>
</html>

