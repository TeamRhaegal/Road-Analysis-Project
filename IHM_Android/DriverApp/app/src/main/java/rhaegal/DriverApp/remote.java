package rhaegal.DriverApp;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattDescriptor;
import android.bluetooth.BluetoothGattService;
import android.bluetooth.BluetoothManager;
import android.bluetooth.BluetoothProfile;
import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.PorterDuff;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import java.lang.reflect.Method;
import java.util.List;
import java.util.UUID;

import io.github.controlwear.virtual.joystick.android.JoystickView;

import static android.bluetooth.BluetoothDevice.TRANSPORT_LE;

public class remote extends AppCompatActivity {

    private final static String TAG = remote.class.getSimpleName();

    //btGatt variables
    private BluetoothGatt btGatt;
    private BluetoothDevice btDevice;
    private BluetoothGattCharacteristic transmitterCharacteristic = null;
    private BluetoothGattCharacteristic receiverCharacteristic = null;

    //state variables
    private boolean started;
    private boolean connected;
    private boolean turboed;
    private boolean autonomous;
    private boolean driving;
    private String joystickValue;

    //view variables
    private Button connect;
    private Button auto;
    private Button start;
    private Button turbo;
    private JoystickView joystick;
    private ImageView direction;
    private ImageView sonar;
    private ImageView battery;
    private ImageView car;
    private TextView speed;


    /**
     * Finds all the objects in the view, link them to lacal variables
     * call methods to set bluetooth, buttons and joystick
     * initialize state
     *
     * @param savedInstanceState previous sate in case of close or pause
     */
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.remote);
        //Log.i(TAG, "Create\n");

        auto = findViewById(R.id.autonomous);
        connect = findViewById(R.id.connect);
        start = findViewById(R.id.move);
        turbo = findViewById(R.id.turbo);
        joystick = findViewById(R.id.joystick);
        direction = findViewById(R.id.direction);
        sonar = findViewById(R.id.sonar);
        battery = findViewById(R.id.battery);
        speed = findViewById(R.id.speed);
        car = findViewById(R.id.car);

        setBt();

        setConnectButton();
        setStartButton();
        setAutoButton();
        setTurboButton();
        setJoystick();

        speed.setText(R.string.speed);

        started = false;
        connected = false;
        autonomous = false;
        turboed = false;
        driving = false;
        joystickValue = Constants.NOTHING;

    }

    /////////////////////////////////////////////////////////////////////////////
    //setup

    /**
     * gets the address of the device to connect to
     * creates the bluetooth manager service from the system and adapter
     * initializes the bluetooth device, and btGatt to null
     */
    private void setBt() {
        String deviceAddress;
        BluetoothManager btManager;
        BluetoothAdapter btAdapter;
        final Intent intent = getIntent();
        deviceAddress = intent.getStringExtra(Constants.EXTRAS_DEVICE_ADDRESS);
        btManager = (BluetoothManager) getSystemService(Context.BLUETOOTH_SERVICE);
        btAdapter = btManager.getAdapter();
        btDevice = btAdapter.getRemoteDevice(deviceAddress);
        btGatt = null;
    }

    /**
     * Initializes the Connect button
     * adds an on click listener for the button
     * sets the actions executed by the button:
     * connect and disconnect
     * change state variables
     * change buttons text and color depending on the state
     * resets the dashbord and joystick
     */
    private void setConnectButton() {
        //Connect button
        connected = false;
        connexionChange();
        connect.getBackground().setColorFilter(Color.parseColor(Constants.night), PorterDuff.Mode.MULTIPLY);
        //Log.i(TAG, "Buttons\n");

        connect.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                if (connected) {
                    sendMessage(Constants.CONNECTION,Constants.OFF);
                    if (btGatt != null) {
                        btGatt.disconnect();
                    }
                    //Log.i(TAG, "disconnect\n");
                } else {
                    if (btGatt == null) {
                        Toast.makeText(remote.this, "Trying to connect", Toast.LENGTH_LONG).show();
                        connect.setText(R.string.connecting);
                        btGatt = btDevice.connectGatt(remote.this, false, gattCallback, TRANSPORT_LE);
                        if(!refreshDeviceCache(btGatt)){
                            Toast.makeText(remote.this, "Can't refresh", Toast.LENGTH_SHORT).show();
                        }
                    }
                    //Log.i(TAG, "connect\n");
                }
            }
        });
    }

    /**
     * Initializes the Autonomous button
     * adds an on click listener for the button
     * sets the actions executed by the button:
     * change state variables
     * change buttons texts and colors depending on the state
     * resets the dashbord and joystick
     */
    private void setAutoButton() {
        //auto button
        auto.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                if (connected) {
                    if (autonomous) {
                        auto.setText(R.string.manual);
                        autonomous = false;
                        started = false;
                        turboed = false;
                        driving = false;
                        resetSymbols();
                        //Log.i(TAG, "manual\n");
                        start.setText(R.string.start);
                        start.getBackground().setColorFilter(Color.parseColor(Constants.blue), PorterDuff.Mode.MULTIPLY);
                        turbo.getBackground().setColorFilter(Color.parseColor(Constants.blue), PorterDuff.Mode.MULTIPLY);
                        sendMessage(Constants.MODE,Constants.ASSISTED);
                    } else {
                        auto.setText(R.string.autonomous);
                        autonomous = true;
                        started = false;
                        turboed = false;
                        driving = false;
                        joystickValue = Constants.NOTHING;
                        resetSymbols();
                        //Log.i(TAG, "autonomous\n");
                        start.setText(R.string.start);
                        start.getBackground().setColorFilter(Color.parseColor(Constants.ice), PorterDuff.Mode.MULTIPLY);
                        turbo.getBackground().setColorFilter(Color.parseColor(Constants.ice), PorterDuff.Mode.MULTIPLY);
                        sendMessage(Constants.MODE,Constants.AUTONOMOUS);
                    }
                }
            }
        });
    }

    /**
     * Initializes the Start button
     * adds an on click listener for the button
     * sets the actions executed by the button:
     * change state variables
     * change button text depending on the state
     * resets the dashbord and joystick
     * activates the joystick depending on the state
     */
    private void setStartButton() {
        //start button
        start.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                if (connected) {
                    if (!autonomous){
                        if (started) {
                            start.setText(R.string.start);
                            started = false;
                            turboed = false;
                            driving = false;
                            joystickValue = Constants.NOTHING;
                            resetSymbols();
                            //Log.i(TAG, "stop\n");
                            turbo.getBackground().setColorFilter(Color.parseColor(Constants.blue), PorterDuff.Mode.MULTIPLY);
                            sendMessage(Constants.STATE,Constants.OFF);
                        } else {
                            start.setText(R.string.stop);
                            turbo.getBackground().setColorFilter(Color.parseColor(Constants.blue), PorterDuff.Mode.MULTIPLY);
                            started = true;
                            resetSymbols();
                            //Log.i(TAG, "start\n");
                            joystick.setEnabled(true);
                            joystick.invalidate();
                            sendMessage(Constants.STATE,Constants.ON);
                        }
                    }
                }
            }
        });
    }

    /**
     * Initializes the Turbo button
     * adds an on click listener for the button
     * sets the actions executed by the button:
     * change state variables
     * change button text and color depending on the state
     */
    private void setTurboButton() {
        //turbo button
        turbo.setText(R.string.turbo);
        turbo.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                if (connected) {
                    if (!autonomous){
                        if (started) {
                            if (turboed) {
                                turbo.getBackground().setColorFilter(Color.parseColor(Constants.blue), PorterDuff.Mode.MULTIPLY);
                                turboed = false;
                                //Log.i(TAG, "turbo off\n");
                                sendMessage(Constants.TURBO,Constants.OFF);
                            } else {
                                turbo.getBackground().setColorFilter(Color.parseColor(Constants.purple), PorterDuff.Mode.MULTIPLY);
                                turboed = true;
                                //Log.i(TAG, "turbo on\n");
                                sendMessage(Constants.TURBO,Constants.ON);
                            }
                        }
                    }
                }
            }
        });
    }

    /**
     * Initializes the Joystick button
     * adds an on move listener for the joystick every 200ms
     * sets the actions executed by the joystick:
     * change state variable driving
     * changes the angle value
     * sets the refresh rate to 50 ms
     */
    private void setJoystick() {
        joystick.setOnMoveListener(new JoystickView.OnMoveListener() {

            @Override
            public void onMove(int angle, int strength) {
                if (connected) {
                    if (started) {
                        if (strength > 50) {
                            driving = true;
                        }
                        if (strength < 50 & driving) {
                            driving = false;
                            //Log.i(TAG, "stopped");
                        }
                        computeJoystickValue(angle);
                    }
                }
            }
        }, 50);
    }

    ////////////////////////////////////////////////////////////////////////////////
    //callbacks
    public final BluetoothGattCallback gattCallback = new BluetoothGattCallback() {

        /**
         * Callback indicating when GATT client has connected/disconnected to/from a remote GATT server.
         *
         * @param  gatt   GATT client
         * @param  status Status of the connect or disconnect operation. GATT_SUCCESS if the operation succeeds
         * @param  newState Returns the new connection state. Can be one of STATE_DISCONNECTED or STATE_CONNECTED
         */
        @Override
        public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {
            if (newState == BluetoothProfile.STATE_CONNECTED) {
                resetSymbols();
                connected = true;
                connexionChange();
                //Log.i(TAG, "Connected to GATT server\n");
                btGatt.requestConnectionPriority(BluetoothGatt.CONNECTION_PRIORITY_HIGH);
                btGatt.discoverServices();
            } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                resetSymbols();
                connected = false;
                connexionChange();
                //Log.i(TAG, "Disconnected from GATT server\n");
                if (btGatt != null) {
                    btGatt.close();
                    btGatt = null;
                }
            }

        }

        /**
         * Callback invoked when the list of remote services, characteristics and descriptors for the remote device
         * have been updated, ie new services have been discovered.
         * searches for the awaited service and characteristics
         * initializes the bluetooth variables associates to service and characteristics
         *
         * @param  gatt   GATT client
         * @param  status Status of the connect or disconnect operation. GATT_SUCCESS if the operation succeeds
         */
        @Override
        public void onServicesDiscovered(BluetoothGatt gatt, int status) {
            if (status != BluetoothGatt.GATT_SUCCESS) {
                gatt.disconnect();
                btGatt = null;
                return;
            }
            //Log.i(TAG, "service discovered\n");
            List<BluetoothGattService> services = gatt.getServices();
            String uuid;
            // Loop through available GATT Services.
            for (BluetoothGattService gattService : services) {
                uuid = gattService.getUuid().toString();
                //Log.i(TAG, uuid + "\n");
                if (uuid.equals(Constants.uuidRemoteService)) {
                    //Log.i(TAG, "found uuid\n");
                    List<BluetoothGattCharacteristic> gattCharacteristics = gattService.getCharacteristics();
                    Toast.makeText(remote.this, "Found the targeted service", Toast.LENGTH_SHORT).show();
                    // Loop through available Characteristics.
                    for (BluetoothGattCharacteristic gattCharacteristic : gattCharacteristics) {
                        uuid = gattCharacteristic.getUuid().toString();
                        //Log.i(TAG, uuid + "\n");
                        if (uuid.equals(Constants.uuidTransmitterCharacteristic)) {
                            transmitterCharacteristic = gattCharacteristic;
                            Toast.makeText(remote.this, "Found the targeted characteristics", Toast.LENGTH_SHORT).show();
                            sendMessage(Constants.CONNECTION,Constants.ON);

                            //Log.i(TAG, "found state\n");
                        } else if (uuid.equals(Constants.uuidReceiverCharacteristic)) {
                            receiverCharacteristic = gattCharacteristic;
                            //Log.i(TAG, "found feedback\n");
                        }
                    }
                    enableNotification(btGatt);
                }
            }
        }

        /**
         * Callback triggered as a result of a remote characteristic notification.
         * calls functions associated with dashboard element that need to be updated
         *
         * @param  gatt   GATT client the characteristic is associated with
         * @param  characteristic Characteristic that has been updated as a result of a remote notification event.
         */
        @Override
        public void onCharacteristicChanged(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic) {
            //Log.i(TAG, "notification!");
            final String data = characteristic.getStringValue(0);
            //Log.i(TAG, "data: " + data + "\n");

            String[] dataSplitted = data.split("$");
            String key = dataSplitted[0];
            String value = dataSplitted[1];

            switch (key) {
                case Constants.MODE :
                    changeMode(value);
                    break;
                case Constants.BATTERY :
                    changeBatt(value);
                    break;
                case Constants.DIRECTION :
                    changeDir(value);
                    break;
                case Constants.RADAR :
                    changeSonar(value);
                    break;
                case Constants.ROUTE :
                    changeCar(value);
                    break;
                case Constants.SPEED:
                    changeSpeed(value);
                    break;

            }
        }
    };

    ////////////////////////////////////////////////////////////////////////////////
    //Bluetooth functions

    /**
     * Function refreshing the bluetooth device cache
     * @param gatt GATT client the device is associated with
     * @return boolean indicating the success or failure of the refresh procedure
     */
    private boolean refreshDeviceCache(BluetoothGatt gatt){
        try {
            Method refresh = gatt.getClass().getMethod("refresh");
            if (refresh != null) {
                return (Boolean) refresh.invoke(gatt);
            }
        }
        catch (Exception localException) {
            Log.e(TAG, "An exception occured while refreshing device");
        }
        return false;
    }

    /**
     * Function changing the UI and changing state variables according to the connection state
     */
    private void connexionChange() {
        if (connected) {
            started = false;
            turboed = false;
            autonomous = false;
            driving = false;
            joystickValue = Constants.NOTHING;
            runOnUiThread(new Runnable() {
                public void run() {
                    auto.getBackground().setColorFilter(Color.parseColor(Constants.blue), PorterDuff.Mode.MULTIPLY);
                    start.getBackground().setColorFilter(Color.parseColor(Constants.blue), PorterDuff.Mode.MULTIPLY);
                    turbo.getBackground().setColorFilter(Color.parseColor(Constants.blue), PorterDuff.Mode.MULTIPLY);
                    start.setText(R.string.start);
                    auto.setText(R.string.manual);
                    connect.setText(R.string.disconnect);
                }
            });
        } else {
            started = false;
            turboed = false;
            autonomous = false;
            driving = false;
            joystickValue = Constants.NOTHING;
            runOnUiThread(new Runnable() {
                public void run() {
                    auto.getBackground().setColorFilter(Color.parseColor(Constants.ice), PorterDuff.Mode.MULTIPLY);
                    start.getBackground().setColorFilter(Color.parseColor(Constants.ice), PorterDuff.Mode.MULTIPLY);
                    turbo.getBackground().setColorFilter(Color.parseColor(Constants.ice), PorterDuff.Mode.MULTIPLY);
                    start.setText(R.string.start);
                    auto.setText(R.string.manual);
                    connect.setText(R.string.connect);
                }
            });
            transmitterCharacteristic = null;
            receiverCharacteristic = null;
        }
    }

    /**
     * Function enabling Notification for a characteristic and creating the associated descriptor.
     *
     * @param gatt GATT client the characteristic is associated with
     */
    private void enableNotification(BluetoothGatt gatt) {
        if (receiverCharacteristic != null) {
            boolean result;
            BluetoothGattCharacteristic characteristic = receiverCharacteristic;
            gatt.setCharacteristicNotification(characteristic, true);
            // 0x2902 org.bluetooth.descriptor.gatt.client_characteristic_configuration.xml
            UUID uuid = UUID.fromString("00002902-0000-1000-8000-00805f9b34fb");
            BluetoothGattDescriptor descriptor = characteristic.getDescriptor(uuid);
            descriptor.setValue(BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE);
            result = gatt.writeDescriptor(descriptor);
            if (result) {
                //Log.i(TAG, "feedback notification enabled\n");
            } else {
                //Log.i(TAG, "feedback notification not enabled\n");
            }
        }

    }

    ////////////////////////////////////////////////////////////////////////////////
    //Symbol functions

    /**
     * Function resetting all symbols to their rest appearance
     */
    public void resetSymbols() {
        runOnUiThread(new Runnable() {
            public void run() {
                joystick.setEnabled(false);
                joystick.resetButtonPosition();
                joystick.invalidate();
                joystickValue = Constants.NOTHING;
                direction.setImageResource(R.drawable.ic_direction_ice);
                sonar.setImageResource(R.drawable.ic_sonar);
                battery.setImageResource(R.drawable.ic_batt_full);
                car.setImageResource(R.drawable.ic_car);
                String conSpeedString = 0.0 + " km/h";
                speed.setText(conSpeedString);

            }
        });
    }

    /**
     * Function updating mode
     *
     * @param modeValue mode: true = autonomous, false = manual
     */
    private void changeMode(final String modeValue) {
        runOnUiThread(new Runnable() {
            public void run() {
                if (modeValue.equals(Constants.AUTONOMOUS) & !autonomous) {
                    auto.setText(R.string.autonomous);
                    autonomous = true;
                    started = false;
                    turboed = false;
                    driving = false;
                    joystickValue = Constants.NOTHING;
                    resetSymbols();
                    //Log.i(TAG, "autonomous\n");
                    start.setText(R.string.start);
                    turbo.getBackground().setColorFilter(Color.parseColor(Constants.ice), PorterDuff.Mode.MULTIPLY);
                    start.getBackground().setColorFilter(Color.parseColor(Constants.ice), PorterDuff.Mode.MULTIPLY);

                } else if (modeValue.equals(Constants.ASSISTED) & autonomous) {

                    auto.setText(R.string.manual);
                    autonomous = false;
                    started = false;
                    turboed = false;
                    driving = false;
                    joystickValue = Constants.NOTHING;
                    resetSymbols();
                    //Log.i(TAG, "manual\n");
                    start.setText(R.string.start);
                    turbo.getBackground().setColorFilter(Color.parseColor(Constants.blue), PorterDuff.Mode.MULTIPLY);
                    start.getBackground().setColorFilter(Color.parseColor(Constants.blue), PorterDuff.Mode.MULTIPLY);
                }
            }
        });
    }

    /**
     * Function updating direction indicators according to wheel direction
     *
     * @param directionValue wheel direction
     */
    private void changeDir(final String directionValue) {

        //Log.i(TAG, "change direction\n");
        runOnUiThread(new Runnable() {
            public void run() {
                switch (directionValue) {
                    case Constants.FRONT:
                        direction.setImageResource(R.drawable.ic_direction_front);
                        break;
                    case Constants.LEFT:
                        direction.setImageResource(R.drawable.ic_direction_left);
                        break;
                    case Constants.RIGHT:
                        direction.setImageResource(R.drawable.ic_direction_right);
                        break;
                    case Constants.NOTHING:
                        direction.setImageResource(R.drawable.ic_direction_ice);
                        break;
                }
            }
        });
    }

    /**
     * Function updating speed indicator in hm/h according to vehicle speed
     *
     * @param speedValue vehicle speed in m/s
     */
    private void changeSpeed(String speedValue) {
        int speedValueInt = Integer.valueOf(speedValue);
        java.text.DecimalFormat df = new java.text.DecimalFormat("0.#");
        double convSpeedValue = speedValueInt * 0.36;
        final String conSpeedString = df.format(convSpeedValue) + " km/h";
        runOnUiThread(new Runnable() {
            public void run() {
                speed.setText(conSpeedString);
            }
        });
    }


    /**
     * Function updating battery indicators according to battery level
     *
     * @param batteryValue battery level
     */
    private void changeBatt(final String batteryValue) {
        runOnUiThread(new Runnable() {
            public void run() {
                switch (batteryValue) {
                    case Constants.MIDDLE:
                        battery.setImageResource(R.drawable.ic_batt_mid);
                        break;
                    case Constants.LOW:
                        battery.setImageResource(R.drawable.ic_batt_low);
                        break;
                    case Constants.CRITICAL:
                        battery.setImageResource(R.drawable.ic_batt_critical);
                        break;
                }
            }
        });
    }

    /**
     * Function updating obstacle presence indicators according to sonar value
     *
     * @param sonarValue presence localization
     */
    private void changeSonar(final String sonarValue) {
        runOnUiThread(new Runnable() {
            public void run() {
                switch (sonarValue) {
                    case Constants.RIGHT:
                        //presence right
                        sonar.setImageResource(R.drawable.ic_sonar_right);
                        break;
                    case Constants.FRONT:
                        //presence front
                        sonar.setImageResource(R.drawable.ic_sonar_front);
                        break;
                    case (Constants.FRONT+"&"+Constants.RIGHT):
                        //presence front and right
                        sonar.setImageResource(R.drawable.ic_sonar_right_front);
                        break;
                    case Constants.LEFT:
                        //presence left
                        sonar.setImageResource(R.drawable.ic_sonar_left);
                        break;
                    case (Constants.RIGHT+"&"+Constants.LEFT):
                        //presence left and right
                        sonar.setImageResource(R.drawable.ic_sonar_left_right);
                        break;
                    case (Constants.FRONT+"&"+Constants.LEFT):
                        //presence left and front
                        sonar.setImageResource(R.drawable.ic_sonar_left_front);
                        break;
                    case (Constants.FRONT+"&"+Constants.RIGHT+"&"+Constants.LEFT):
                        //presence left front and right;
                        sonar.setImageResource(R.drawable.ic_sonar_left_right_front);
                        break;
                    case Constants.NOTHING:
                        sonar.setImageResource(R.drawable.ic_sonar);
                        break;
                }
            }
        });
    }

    /**
     * Function updating road side indicators according to edge distance
     *
     * @param carValue road side
     */
    private void changeCar(final String carValue) {
        runOnUiThread(new Runnable() {
            public void run() {
                switch (carValue) {
                    case Constants.RIGHT:
                        //car drifting right
                        car.setImageResource(R.drawable.ic_car_right);
                        break;
                    case (Constants.RIGHT+"&"+Constants.CRITICAL):
                        //car critically right
                        car.setImageResource(R.drawable.ic_car_right_critical);
                        break;
                    case Constants.LEFT:
                        //car drifting left
                        car.setImageResource(R.drawable.ic_car_left);
                        break;
                    case (Constants.LEFT+"&"+Constants.CRITICAL):
                        //car critically left
                        car.setImageResource(R.drawable.ic_car_left_critical);
                        break;
                    case Constants.NOTHING:
                        car.setImageResource(R.drawable.ic_car);
                        break;
                }
            }
        });
    }


    ////////////////////////////////////////////////////////////////////////////////
    //message sending

    /**
     * Function calculating joystick direction from joystick angle
     *
     * @param joystick_angle joystick direction
     */
    private void computeJoystickValue(int joystick_angle) {
        String joystickCurrentValue="";
        if (driving) {
            if (joystick_angle <= 20 | joystick_angle > 340)
                joystickCurrentValue = Constants.RIGHT;
            else if (joystick_angle <= 65 & joystick_angle > 20)
                joystickCurrentValue = Constants.FRONT+"&"+Constants.RIGHT;
            else if (joystick_angle <= 110 & joystick_angle > 65)
                joystickCurrentValue = Constants.FRONT;
            else if (joystick_angle <= 155 & joystick_angle > 110)
                joystickCurrentValue = Constants.FRONT+"&"+Constants.LEFT;
            else if (joystick_angle <= 200 & joystick_angle > 155)
                joystickCurrentValue = Constants.LEFT;
            else
                joystickCurrentValue = Constants.NOTHING;
        } else {
            joystickCurrentValue = Constants.NOTHING;
        }
        if (!joystickCurrentValue.equals(joystickValue)){
            joystickValue=joystickCurrentValue;
            sendMessage(Constants.JOYSTIC,joystickCurrentValue);
        }
    }

    private void sendMessage(String key, String value){
        if (btGatt != null) {
            if (connected && transmitterCharacteristic != null) {
                String message = key + "$" + value;
                //Log.i(TAG, "to send: " + message + "\n");
                transmitterCharacteristic.setValue(message);
                transmitterCharacteristic.setWriteType(BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE);
                btGatt.writeCharacteristic(transmitterCharacteristic);
            }
        }
    }


}
