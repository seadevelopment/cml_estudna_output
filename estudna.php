<?php

/**
 * CML - How to get value of water level for you eStudna device
 * 
 * 2022-05-17 v1-01
 * a) Project foundation
 */

// ----------------------------------------------------------------------------
// --- Configuration
// ----------------------------------------------------------------------------

// --- Configuration
$user = 'zakaznik@email.com';
$password = 'heslo';
$sn = 'SB819098';   // Serial number of your eSTUDNA



// ----------------------------------------------------------------------------
// --- Code
// ----------------------------------------------------------------------------

function httpPost($url,$data,$header)
{
    
    // use key 'http' even if you send the request to https://...
    $options = array
    (
        'http' => array
        (
            'header'  => 'Content-Type: application/json\r\n' . $header,
            'method'  => 'POST',
            'content' => json_encode($data)
        )
    );
    $context  = stream_context_create($options);
    $result = file_get_contents($url, false, $context);

    if ($result === FALSE)
    {
        throw new Exception('HTTP request failed!');
    }

    return $result;
}

function httpGet($url,$header)
{
    
    // use key 'http' even if you send the request to https://...
    $options = array
    (
        'http' => array
        (
            'header'  => $header,
            'method'  => 'GET',
        )
    );
    $context  = stream_context_create($options);
    $result = file_get_contents($url, false, $context);

    if ($result === FALSE)
    {
        throw new Exception('HTTP request failed!');
    }

    return $result;
}

/**
 * Objekt pro pristup k Thingsboardu
 */
class ThingsBoard
{
    public $server =  'https://cml.seapraha.cz';
    public $userToken = null;
    public $customerId = null;

    /**
     * Prihlaseni uzivatele
     */
    public function login($user,$password)
    {
        // Login
        $url = $this->server . '/api/auth/login';
        $result = httpPost($url,array('username' => $user, 'password' => $password),"");

        $response = json_decode($result);
        $this->userToken = $response->token;    // User token

        // Get customer ID
        $url = $this->server . '/api/auth/user';
        $result = httpGet($url,'X-Authorization: Bearer ' . $this->userToken );
        
        $response = json_decode($result);
        $this->customerId = $response->customerId->id; // Customer ID
            
    }

    /**
     * Vyhledani zarizeni podle nazvu
     */
    public function getDevicesByName($name)
    {
        $url = $this->server . '/api/customer/' . $this->customerId . '/devices?pageSize=100&page=0&&textSearch='.urlencode($name);
        
        $result = httpGet($url, 'X-Authorization: Bearer ' . $this->userToken);
        $response = json_decode($result);
        if ($response->totalElements < 1)
            throw new Exception('Device SN ' . $name . ' has not been found!');

        return $response->data;         // Return list of devices
    }


    public function setDeviceOutput($deviceId, $output, $value)
    {
        if ($output == 'OUT1') 
        {
            $output = 'setDout1';
        } else
        {
            $output = 'setDout2';
        }
        $data = array(
            "method" => $output,
            "params" => $value
        );
        $url = $this->server . '/api/rpc/twoway/' . $deviceId;
        
        httpPost($url, $data, 'X-Authorization: Bearer ' . $this->userToken);
    }
}


function eStudna_SetOutput($user, $password, $serialNumber, $output, $value)
{
    $tb = new ThingsBoard();
    $tb->login($user,$password);
    $devices = $tb->getDevicesByName( '%' . $serialNumber);
    $tb->setDeviceOutput($devices[0]->id->id, $output, $value);
}


// ----------------------------------------------------------------------------
// --- Main code
// ----------------------------------------------------------------------------

try
{
  echo('<pre><b>' . $sn . '</b></pre>');
  echo('<pre>OUT1: true</pre>');
  eStudna_SetOutput($user, $password, $sn, "OUT1", False);
  echo('<pre>OUT1: false</pre>');
  sleep(1);
  eStudna_SetOutput($user, $password, $sn, "OUT1", True);
  echo('<pre>OUT1: true</pre>');
} catch (Exception $e) {
    echo('<pre>[ EXCEPTION] - ' . $e->getMessage() . '</pre>');
}

?>
