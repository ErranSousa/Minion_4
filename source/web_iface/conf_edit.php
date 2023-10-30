<!DOCTYPE html>
<html>
<head>
<title>Edit XXX Config</title>
<style>
    body {
        width: 35em;
        margin: 0 auto;
        font-family: Tahoma, Verdana, Arial, sans-serif;
    	/*background-color:lightskyblue;*/
    }
</style>
</head>
<body>
<h1>MINION XXX Config!</h1>

<p>This tool is designed to prepare MINIONs for deployment</p>

<?php

$cfg_file = parse_ini_file("/home/pi/Desktop/Minion_config.ini", true);

if ($cfg_file['Sampling_scripts']['image'] == 1) { $Image = "checked";} else { $Image = "";}
if ($cfg_file['Sampling_scripts']['30Ba-pres'] == 1) { $BA30 = "checked";} else { $BA30 = "";}
if ($cfg_file['Sampling_scripts']['100Ba-pres'] == 1) { $BA100 = "checked";} else { $BA100 = "";}
if ($cfg_file['Sampling_scripts']['temperature'] == 1) { $Temp = "checked";} else { $Temp = "";}
if ($cfg_file['Sampling_scripts']['oxybase'] == 1) { $OXY = "checked";} else { $OXY = "";}

echo '<form action="/action_page.php" method="post">
  <label for="DMAX">Maximum Depth:</label>
  <br>
  <input type="text" id="DMAX" name="DMAX" size="6" style="text-align:right" value="'.$cfg_file['Mission']['max_depth'].'"> meters<br>
  <br>
  <fieldset>
  <legend><b>Sensors</b></legend>
  <input '.$Image.' type="checkbox" id="Image" name="Image" value="Image">
  <label for="Image"> Image</label><br>
  <input '.$BA30.' type="checkbox" id="30Bar_Pres" name="30Bar_Pres" value="30Bar_Pres">
  <label for="30Bar_Pres"> BR 30 Bar Pressure Sensor</label><br>
  <input '.$BA100.' type="checkbox" id="100Bar_Pres" name="100Bar_Pres" value="100Bar_Pres">
  <label for="100Bar_Pres"> BR 100 Bar Pressure Sensor</label><br>
  <input '.$Temp.' type="checkbox" id="Temp" name="Temp" value="Temp">
  <label for="Temp"> BR Temperature Sensor</label><br>
  <input '.$OXY.' type="checkbox" id="OXY" name="OXY" value="OXY">
  <label for="OXY"> Oxybase O2 Sensor</label><br>
  </fieldset>
  <br>
  <fieldset>
  <legend><b>Initial Sampling Mode</b></legend>
  <br>
  <label for="IHours">Total Mode Duration:</label><br>
  <input type="text" id="IHours" name="IHours" size="6" style="text-align:right" value="'.$cfg_file['Initial_Samples']['hours'].'"> hours<br>
  <br>
  <label for="ICamFS">Image Capture Period:</label><br>
  <input type="text" id="ICamFS" name="ICamFS" size="6" style="text-align:right" value="'.$cfg_file['Initial_Samples']['camera_sample_period'].'"> minutes<br>
  <br>
  <label for="ITPFS">Temperature and Pressure Sample Period:</label><br>
  <input type="text" id="ITPFS" name="ITPFS" size="6" style="text-align:right" value="'.$cfg_file['Initial_Samples']['temppres_sample_period'].'"> seconds<br>
  <br>
  <label for="IOXYFS">OxyBase Sample Period:</label><br>
  <input type="text" id="IOXYFS" name="IOXYFS" size="6" style="text-align:right" value="'.$cfg_file['Initial_Samples']['oxygen_sample_period'].'"> seconds<br>
  <br>
  </fieldset>
  <br>
  <fieldset>
  <legend><b>Time Lapse Sampling Mode</b></legend>
  <p style="color:red;"><em>Note: If (Sample Burst Interval - Sample Burst Duration) < 2 minutes, the system will not enter low power mode between sample bursts.</em></p>
  <label for="THours">Total Mode Duration:</label><br>
  <input type="text" id="THours" name="THours" size="6" style="text-align:right" value="'.$cfg_file['Time_Lapse_Samples']['hours'].'"> hours<br>
  <br>
  <label for="DS_Time">Sample Burst Duration:</label><br>
  <input type="text" id="DS_Time" name="DS_Time" size="6" style="text-align:right" value="'.$cfg_file['Time_Lapse_Samples']['sample_burst_duration'].'"> minutes<br>
  <br>
  <label for="DS_Interval">Sample Burst Interval:</label><br>
  <input type="text" id="DS_Interval" name="DS_Interval" size="6" style="text-align:right" value="'.$cfg_file['Time_Lapse_Samples']['sample_interval_minutes'].'"> minutes<br>
  <br>
  <label for="TCamFS">Image Capture Period:</label><br>
  <input type="text" id="TCamFS" name="TCamFS" size="6" style="text-align:right" value="'.$cfg_file['Time_Lapse_Samples']['camera_sample_period'].'"> minutes<br>
  <br>
  <label for="SensorFS">Temperature and Pressure Sample Period:</label><br>
  <input type="text" id="SensorFS" name="SensorFS" size="6" style="text-align:right" value="'.$cfg_file['Time_Lapse_Samples']['temppres_sample_period'].'"> seconds<br>
  <br>
  <label for="OxygenFS">OxyBase Sample Period:</label><br>
  <input type="text" id="OxygenFS" name="OxygenFS" size="6" style="text-align:right" value="'.$cfg_file['Time_Lapse_Samples']['oxygen_sample_period'].'"> seconds<br>
  <br>
  </fieldset>
  <br>
  <fieldset>
  <legend><b>Final Sampling Mode</b></legend>
  <br>
  <label for="FHours">Total Mode Duration:</label><br>
  <input type="text" id="FHours" name="FHours" size="6" style="text-align:right" value="'.$cfg_file['Final_Samples']['hours'].'"> hours<br>
  <br>
  <label for="FCamFS">Image Capture Period:</label><br>
  <input type="text" id="FCamFS" name="FCamFS" size="6" style="text-align:right" value="'.$cfg_file['Final_Samples']['camera_sample_period'].'"> minutes<br>
  <br>
  <label for="FTPFS">Temperature and Pressure Sample Period:</label><br>
  <input type="text" id="FTPFS" name="FTPFS" size="6" style="text-align:right" value="'.$cfg_file['Final_Samples']['temppres_sample_period'].'"> seconds<br>
  <br>
  <label for="FOXYFS">OxyBase Sample Period:</label><br>
  <input type="text" id="FOXYFS" name="FOXYFS" size="6" style="text-align:right" value="'.$cfg_file['Final_Samples']['oxygen_sample_period'].'"> seconds<br>
  <br>
  </fieldset>
  <br>
  <fieldset>
  <legend><b>GPS Transmission Window Settings</b></legend>
  <br>
  <label for="gps_dur_hrs">GPS Transmission Window Duration:</label><br>
  <input type="text" id="gps_dur_hrs" name="gps_dur_hrs" size="6" style="text-align:right" value="'.$cfg_file['GPS']['gps_transmission_window'].'"> hours<br>
  <br>
  <label for="gps_interval_min">GPS Position Interval:</label><br>
  <input type="text" id="gps_interval_min" name="gps_interval_min" size="6" style="text-align:right" value="'.$cfg_file['GPS']['gps_transmission_interval'].'"> minutes<br>
  <br>
  </fieldset>
  <br>
  <fieldset>
  <legend><b>Ignore WIFI Signal</b></legend>
  <br>
  <input type="text" id="IG_WIFI-hours" name="IG_WIFI-hours" size="6" style="text-align:right" value="'.$cfg_file['Mission']['ignore_wifi-hours'].'"> hours<br>
  <br>
  </fieldset>
  <br>
  <fieldset>
  <legend><b>Confirm Minion Number</b></legend>
  <input type="text" id="MNumber" name="MNumber" size="6" style="text-align:right" value="'.$cfg_file['MINION']['number'].'"  required/>
  </fieldset>
  <br>
  <input type="submit" value="Review">
  <input type="reset">
</form>';

?>

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
<br>
<br>
