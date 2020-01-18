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
import android.content.DialogInterface;
import android.content.Intent;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.PorterDuff;
import android.os.CountDownTimer;
import android.os.Environment;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Collections;
import java.util.List;
import java.util.StringTokenizer;
import java.util.UUID;

import io.github.controlwear.virtual.joystick.android.JoystickView;

import static android.bluetooth.BluetoothDevice.TRANSPORT_LE;

public class ControlPanel extends AppCompatActivity {

    private final static String TAG = ControlPanel.class.getSimpleName();

    //btGatt variables
    private BluetoothGatt btGatt;
    private BluetoothDevice btDevice;
    private BluetoothGattCharacteristic transmitterCharacteristic = null;
    private BluetoothGattCharacteristic receiverCharacteristic = null;
    private BluetoothGattCharacteristic receiverImgCharacteristic = null;

    //state variables
    private boolean started = false;
    private boolean connected = false;
    private boolean autonomous = false;
    private boolean driving = false;
    private boolean stopSignDetected = false;
    private boolean searchSignDetected = false;
    private String joystickValue = Constants.NOTHING;
    private double speedValue = 0.0;

    //view variables
    private Button connect;
    private Button auto;
    private Button start;
    private JoystickView joystick;
    private TextView speed;
    private Button logButton;
    private ImageView imageStopSign;
    private ImageView imageSearchSign;
    private TextView stopSignAhead;
    private TextView searchSignAhead;
    private ImageView imageCar;
    private ImageView imageSignalFront;
    private ImageView imageAttentionFront;
    private TextView obstacleFront;
    private ImageView imageSignalRear;
    private ImageView imageAttentionRear;
    private TextView obstacleRear;

    //STOP sign
    private AlertDialog dialogEmergencyStop;
    private AlertDialog dialogSearchSign;
    private Boolean emergencyFront = false;
    private Boolean emergencyBack = false;
    private boolean doRecvImgNotif = false;
    private boolean isSendingMesg  = false;



    private byte[] searchImage = new byte[0];
    private int counterSearchImage;
    private List<String> msgTosend = new ArrayList<>();

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

        setContentView(R.layout.control_layout);
        //Log.i(TAG, "Create\n");

        auto = findViewById(R.id.autonomous);
        connect = findViewById(R.id.connect);
        start = findViewById(R.id.move);
        joystick = findViewById(R.id.joystick);
        speed = findViewById(R.id.speed);
        logButton = findViewById(R.id.file);
        imageSearchSign = findViewById(R.id.image_searchsign);
        searchSignAhead = findViewById(R.id.searchsign_text);
        imageStopSign = findViewById(R.id.image_stopsign);
        stopSignAhead = findViewById(R.id.stopsign_text);
        imageCar = findViewById(R.id.image_car);
        imageSignalFront = findViewById(R.id.image_signal_front);
        imageAttentionFront = findViewById(R.id.image_attention_front);
        obstacleFront = findViewById(R.id.attention_front_text);
        imageSignalRear = findViewById(R.id.image_signal_rear);
        imageAttentionRear = findViewById(R.id.image_attention_rear);
        obstacleRear = findViewById(R.id.attention_rear_text);
        counterSearchImage = 0;


        AlertDialog.Builder builderEmergency = new AlertDialog.Builder(ControlPanel.this);
        builderEmergency.setTitle(R.string.emergencyTitle)
                .setCancelable(false)
                .setIcon(R.drawable.attention_icon)
                .setNeutralButton(R.string.ok, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int id) {
                        dialog.cancel();
                    }
                });

        dialogEmergencyStop = builderEmergency.create();

        AlertDialog.Builder builderSearch = new AlertDialog.Builder(ControlPanel.this);
        builderSearch.setMessage(R.string.searchMsg)
                .setTitle(R.string.searchTitle)
                .setCancelable(false)
                .setIcon(R.drawable.stop_sign)
                .setPositiveButton(R.string.yes, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int id) {
                        changeMode(Constants.AUTONOMOUS);
                        dialog.cancel();
                    }
                })
                .setNegativeButton(R.string.no, new DialogInterface.OnClickListener() {
                    public void onClick(DialogInterface dialog, int id) {
                        dialog.cancel();
                    }
                });

        dialogSearchSign = builderSearch.create();

        setBt();

        setConnectButton();
        setStartButton();
        setAutoButton();
        setJoystick();
        setLogButton();
        
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
        if(deviceAddress !=null){
            btManager = (BluetoothManager) getSystemService(Context.BLUETOOTH_SERVICE);
            btAdapter = btManager.getAdapter();
            btDevice = btAdapter.getRemoteDevice(deviceAddress);
            btGatt = null;
        }
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
                    connected =false;
                    constructMessage(Constants.CONNECTION,Constants.OFF);
                }
                else {
                    if (btGatt == null) {
                        connect.setText(R.string.connecting);
                        btGatt = btDevice.connectGatt(ControlPanel.this, false, gattCallback, TRANSPORT_LE);
                    }
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
                        driving = false;
                        joystickValue = Constants.NOTHING;
                        //Log.i(TAG, "manual\n");
                        start.setText(R.string.start);
                        start.getBackground().setColorFilter(Color.parseColor(Constants.green), PorterDuff.Mode.MULTIPLY);
                        constructMessage(Constants.MODE,Constants.ASSISTED);
                    } else {
                        if(emergencyFront){
                            dialogEmergencyStop.setMessage(getString(R.string.emergencyMsgFront));
                            runOnUiThread(new Runnable() {
                                public void run() {
                                    dialogEmergencyStop.show();
                                }
                            });
                        }
                        else {
                            auto.setText(R.string.autonomous);
                            autonomous = true;
                            started = false;
                            driving = false;
                            joystickValue = Constants.NOTHING;
                            resetJoystick();
                            //Log.i(TAG, "autonomous\n");
                            start.setText(R.string.start);
                            start.getBackground().setColorFilter(Color.parseColor(Constants.ice), PorterDuff.Mode.MULTIPLY);
                            constructMessage(Constants.MODE, Constants.AUTONOMOUS);
                        }
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
                if (connected && !autonomous) {
                    if (started) {
                        start.setText(R.string.start);
                        started = false;
                        driving = false;
                        joystickValue = Constants.NOTHING;
                        resetJoystick();
                        start.getBackground().setColorFilter(Color.parseColor(Constants.green), PorterDuff.Mode.MULTIPLY);
                        //Log.i(TAG, "stop\n");
                        constructMessage(Constants.STATE,Constants.OFF);
                    } else {
                        start.setText(R.string.stop);
                        started = true;
                        //Log.i(TAG, "start\n");
                        joystick.setEnabled(true);
                        joystick.invalidate();
                        joystick.setBorderColor(Color.parseColor(Constants.blue));
                        joystick.setBackgroundColor(Color.parseColor(Constants.night));
                        joystick.setButtonColor(Color.parseColor(Constants.ice));
                        start.getBackground().setColorFilter(Color.parseColor(Constants.red), PorterDuff.Mode.MULTIPLY);
                        constructMessage(Constants.STATE,Constants.ON);
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
        }, 100);
    }

    private void setLogButton() {
        logButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                if(!autonomous && !started) {
                    final Intent intent = new Intent(ControlPanel.this, LogDisplay.class);
                    startActivity(intent);
                }
            }
        });
    }

    ////////////////////////////////////////////////////////////////////////////////
    //callbacks
    public final BluetoothGattCallback gattCallback = new BluetoothGattCallback() {

        /**
         * Callback indicating when GATT client has connected/disconnected to/from a remote GATT server.
         *
         * @param gatt     GATT client
         * @param status   Status of the connect or disconnect operation. GATT_SUCCESS if the operation succeeds
         * @param newState Returns the new connection state. Can be one of STATE_DISCONNECTED or STATE_CONNECTED
         */
        @Override
        public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {
            if (newState == BluetoothProfile.STATE_CONNECTED) {
                //Log.i(TAG, "Connected to GATT server\n");
                connexionChange();
                btGatt.requestConnectionPriority(BluetoothGatt.CONNECTION_PRIORITY_HIGH);
                btGatt.discoverServices();
            } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
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
         * @param gatt   GATT client
         * @param status Status of the connect or disconnect operation. GATT_SUCCESS if the operation succeeds
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
                    // Loop through available Characteristics.
                    for (BluetoothGattCharacteristic gattCharacteristic : gattCharacteristics) {
                        uuid = gattCharacteristic.getUuid().toString();
                        //Log.i(TAG, uuid + "\n");
                        switch (uuid) {
                            case Constants.uuidTransmitterCharacteristic:
                                transmitterCharacteristic = gattCharacteristic;
                                break;

                            //Log.i(TAG, "found state\n");
                            case Constants.uuidReceiverCharacteristic:
                                receiverCharacteristic = gattCharacteristic;
                                //Log.i(TAG, "found feedback\n");
                                break;
                            case Constants.uuidImgReceiverCharacteristic:
                                receiverImgCharacteristic = gattCharacteristic;
                                break;
                        }
                    }
                    enableNotification(receiverCharacteristic);
                }
            }

        }

        /**
         * Callback triggered as a result of a remote characteristic notification.
         * calls functions associated with dashboard element that need to be updated
         *
         * @param gatt           GATT client the characteristic is associated with
         * @param characteristic Characteristic that has been updated as a result of a remote notification event.
         */
        @Override
        public void onCharacteristicChanged(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic) {
            //Log.i(TAG, "notification!");
            if (characteristic == receiverCharacteristic) {
                final String data = characteristic.getStringValue(0);
                //Log.i(TAG, "data: " + data + "\n");

                StringTokenizer tokens = new StringTokenizer(data, "$");
                String key = tokens.nextToken();
                String value1 = tokens.nextToken();
                String value2 = "";
                try {
                    value2 = tokens.nextToken();
                } catch (Exception e) {

                }

                switch (key) {
                    case Constants.MODE:
                        changeMode(value1);
                        break;
                    case Constants.SPEED:
                        changeSpeed(value1);
                        break;
                    case Constants.SIGN:
                        advertizeSign(value1, value2);
                        break;
                    case Constants.EMERGENCYSTOP:
                        advertizeEmergency(value1, value2);
                        break;
                    case Constants.OBJECT:
                        objectFound(value1);
                        break;
                }
            } else if (characteristic == receiverImgCharacteristic) {
                final byte[] data = characteristic.getValue();
                getImage(data);
            }
        }

        @Override
        public void onDescriptorWrite(BluetoothGatt gatt,
                                      BluetoothGattDescriptor descriptor,
                                      int status) {
            if (doRecvImgNotif) {
                enableNotification(receiverImgCharacteristic);

            } else {
                connected = true;
                constructMessage(Constants.CONNECTION, Constants.ON);
                runOnUiThread(new Runnable() {
                    public void run() {
                        auto.getBackground().setColorFilter(Color.parseColor(Constants.blue), PorterDuff.Mode.MULTIPLY);
                        start.getBackground().setColorFilter(Color.parseColor(Constants.green), PorterDuff.Mode.MULTIPLY);
                        connect.setText(R.string.disconnect);
                    }
                });
            }
            doRecvImgNotif = false;
        }

        @Override
        public void onCharacteristicWrite (BluetoothGatt gatt,
                                           BluetoothGattCharacteristic characteristic,
                                           int status){
            removeMsgSent();
            if(ckeckRecvMsgList()){
                sendMessage(msgTosend.get(0));
            }else{
                isSendingMesg = false;
                if(!connected){
                    if (btGatt != null) {
                        btGatt.disconnect();
                    }
                }
            }
        }
    };

    ////////////////////////////////////////////////////////////////////////////////
    //Bluetooth functions

    private void objectFound(final String sizeValue){
        switch(sizeValue) {
            case Constants.BIG :
                    runOnUiThread(new Runnable() {
                        public void run() {
                            Toast.makeText(ControlPanel.this, "Found a big object", Toast.LENGTH_LONG).show();
                        }
                    })
                ;
                break;
        case Constants.MEDIUM :
                runOnUiThread(new Runnable() {
                    public void run() {
                        Toast.makeText(ControlPanel.this, "Found a medium object", Toast.LENGTH_LONG).show();
                    }
                });
            break;
        case Constants.SMALL :
            runOnUiThread(new Runnable() {
                public void run() {
                    Toast.makeText(ControlPanel.this, "Found a small object", Toast.LENGTH_LONG).show();
                }
            });
        break;
        }
    }


    /**
     * Function changing the UI and changing state variables according to the connection state
     */
    private void connexionChange() {
        resetSymbols();
        runOnUiThread(new Runnable() {
            public void run() {
                if(connected) {
                    auto.getBackground().setColorFilter(Color.parseColor(Constants.blue), PorterDuff.Mode.MULTIPLY);
                    start.getBackground().setColorFilter(Color.parseColor(Constants.green), PorterDuff.Mode.MULTIPLY);
                    connect.setText(R.string.disconnect);
                }
                else{
                    if(btGatt!=null) {
                        auto.getBackground().setColorFilter(Color.parseColor(Constants.ice), PorterDuff.Mode.MULTIPLY);
                        start.getBackground().setColorFilter(Color.parseColor(Constants.ice), PorterDuff.Mode.MULTIPLY);
                        connect.setText(R.string.connect);
                    }
                }
            }
        });
        started = false;
        autonomous = false;
        driving = false;
        joystickValue = Constants.NOTHING;
        emergencyBack = false;
        emergencyFront = false;
        transmitterCharacteristic = null;
        receiverCharacteristic = null;
        receiverImgCharacteristic = null;
        isSendingMesg = false;
        speedValue = 0.0;
        doRecvImgNotif = false;
        clearMsgSent();
    }

    /**
     * Function enabling Notification for a characteristic and creating the associated descriptor.
     *
     * @param characteristic characteristic to be enabled
     */

    private void enableNotification(BluetoothGattCharacteristic characteristic) {
        UUID uuid = UUID.fromString("00002902-0000-1000-8000-00805f9b34fb");
        doRecvImgNotif = true;
        btGatt.setCharacteristicNotification(characteristic, true);
        BluetoothGattDescriptor descriptor = characteristic.getDescriptor(uuid);

        if(descriptor!=null) {
            descriptor.setValue(BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE);
            if (!btGatt.writeDescriptor(descriptor)) {
                Toast.makeText(ControlPanel.this, "can't write descriptor", Toast.LENGTH_LONG).show();
            }
        }
    }






    ////////////////////////////////////////////////////////////////////////////////
    //Symbol functions

    /**
     * Function resetting all symbols to their rest appearance
     */
    public void resetSymbols() {
        resetJoystick();
        runOnUiThread(new Runnable() {
            public void run() {
                imageCar.setImageResource(R.drawable.car_icon_ice);
                imageAttentionFront.setImageResource(android.R.color.transparent);
                imageAttentionRear.setImageResource(android.R.color.transparent);
                imageSignalFront.setImageResource(android.R.color.transparent);
                imageSignalRear.setImageResource(android.R.color.transparent);
                imageSearchSign.setImageResource(R.drawable.search_sign_ice);
                imageStopSign.setImageResource(R.drawable.stop_sign_ice);
                obstacleFront.setText("");
                obstacleRear.setText("");
                stopSignAhead.setText("");
                searchSignAhead.setText("");
                speed.setText(R.string.speed0);
                start.setText(R.string.start);
                auto.setText(R.string.manual);

            }
        });
    }

    /**
     * Function resetting joystick when it is disabled
     */
    public void resetJoystick() {
        runOnUiThread(new Runnable() {
            public void run() {
                joystick.setEnabled(false);
                joystick.resetButtonPosition();
                joystick.invalidate();
                joystick.setBorderColor(Color.parseColor(Constants.ice));
                joystick.setBackgroundColor(Color.parseColor(Constants.ice));
                joystick.setButtonColor(Color.parseColor(Constants.blueLight));
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
                    driving = false;
                    joystickValue = Constants.NOTHING;
                    resetJoystick();
                    //Log.i(TAG, "autonomous\n");
                    start.setText(R.string.start);
                    start.getBackground().setColorFilter(Color.parseColor(Constants.ice), PorterDuff.Mode.MULTIPLY);
                    constructMessage(Constants.MODE,Constants.AUTONOMOUS);

                } else if (modeValue.equals(Constants.ASSISTED)) {
                    if(autonomous) {
                        auto.setText(R.string.manual);
                        autonomous = false;
                    }
                    else{
                        if (started){
                            resetJoystick();
                            constructMessage(Constants.JOYSTIC,Constants.NOTHING);
                        }
                    }
                    started = false;
                    driving = false;
                    joystickValue = Constants.NOTHING;
                    //Log.i(TAG, "manual\n");
                    start.setText(R.string.start);
                    start.getBackground().setColorFilter(Color.parseColor(Constants.green), PorterDuff.Mode.MULTIPLY);
                }
            }
        });
    }


    /**
     * Function updating speed indicator in hm/h according to vehicle speed
     *
     * @param speedValueStr vehicle speed in m/s
     */
    private void changeSpeed(String speedValueStr) {
        double speedValueDb = Double.valueOf(speedValueStr);
        if (speedValueDb!=speedValue) {
            speedValue = speedValueDb;
            if (speedValueDb != 0) {
                java.text.DecimalFormat df = new java.text.DecimalFormat("##.##");
                double convSpeedValue = speedValueDb * (3.6);
                final String conSpeedString = df.format(convSpeedValue) + " km/h";

                runOnUiThread(new Runnable() {
                    public void run() {
                        speed.setText(conSpeedString);
                    }
                });
            } else {
                runOnUiThread(new Runnable() {
                    public void run() {
                        speed.setText(R.string.speed0);
                    }
                });
            }
        }
    }



    private void advertizeSign(final String signValue,final String stateValue){
        if (signValue.equals(Constants.STOP)){
            if(stateValue.equals(Constants.ON)& !stopSignDetected) {
                stopSignDetected = true;
                runOnUiThread(new Runnable() {
                    public void run() {
                        imageStopSign.setImageResource(R.drawable.stop_sign);
                        stopSignAhead.setText(R.string.ahead);
                    }
                });
            }
            else if (stateValue.equals(Constants.OFF)& stopSignDetected) {
                stopSignDetected = false;
                runOnUiThread(new Runnable() {
                    public void run() {
                        imageStopSign.setImageResource(android.R.color.transparent);
                        stopSignAhead.setText("");
                    }
                });
            }
        }
        if (signValue.equals(Constants.SEARCH)){
            if(stateValue.equals(Constants.ON)& !searchSignDetected) {
                searchSignDetected = true;
                runOnUiThread(new Runnable() {
                    public void run() {
                        imageSearchSign.setImageResource(R.drawable.search_sign);
                        searchSignAhead.setText(R.string.ahead);
                        if(!autonomous){
                            dialogSearchSign.show();
                        }
                    }
                });
            }
            else if (stateValue.equals(Constants.OFF)& searchSignDetected) {
                searchSignDetected = false;
                runOnUiThread(new Runnable() {
                    public void run() {
                        imageSearchSign.setImageResource(android.R.color.transparent);
                        searchSignAhead.setText("");
                    }
                });
            }

        }
    }

    private void advertizeEmergency(final String areaValue,final String stateValue){
        if (areaValue.equals(Constants.FRONT)){
            if (stateValue.equals(Constants.ON)& !emergencyFront){
                emergencyFront = true;
                runOnUiThread(new Runnable() {
                    public void run() {
                        if(!emergencyBack){
                            imageCar.setImageResource(R.drawable.car_icon);
                        }
                        imageSignalFront.setImageResource(R.drawable.signal_icon_front);
                        imageAttentionFront.setImageResource(R.drawable.attention_icon);
                        obstacleFront.setText(R.string.obstacle);
                    }
                });
                if(autonomous) {
                    changeMode(Constants.ASSISTED);
                    dialogEmergencyStop.setMessage(getString(R.string.emergencyMsg));
                    runOnUiThread(new Runnable() {
                        public void run() {
                            dialogEmergencyStop.show();
                        }
                    });
                }

            }
            else if (stateValue.equals(Constants.OFF)& emergencyFront){
                emergencyFront = false;
                runOnUiThread(new Runnable() {
                    public void run() {
                        imageSignalFront.setImageResource(android.R.color.transparent);
                        imageAttentionFront.setImageResource(android.R.color.transparent);
                        obstacleFront.setText("");
                        if(!emergencyBack){
                            imageCar.setImageResource(R.drawable.car_icon_ice);
                        }
                    }
                });
            }
        }
        else if (areaValue.equals(Constants.REAR)){
            if (stateValue.equals(Constants.ON) & !emergencyBack) {
                emergencyBack = true;
                runOnUiThread(new Runnable() {
                    public void run() {
                        if(!emergencyFront){
                            imageCar.setImageResource(R.drawable.car_icon);
                        }
                        imageSignalRear.setImageResource(R.drawable.signal_icon_rear);
                        imageAttentionRear.setImageResource(R.drawable.attention_icon);
                        obstacleRear.setText(R.string.obstacle);
                    }
                });

            } else if (stateValue.equals(Constants.OFF) & emergencyBack) {
                emergencyBack = false;
                runOnUiThread(new Runnable() {
                    public void run() {
                        imageSignalRear.setImageResource(android.R.color.transparent);
                        imageAttentionRear.setImageResource(android.R.color.transparent);
                        obstacleRear.setText("");
                        if(!emergencyFront){
                            imageCar.setImageResource(R.drawable.car_icon_ice);
                        }
                    }
                });

            }
        }
    }

    private void getImage(final byte[] dataValue){
        if (counterSearchImage < 309){
            ByteArrayOutputStream outputStream = new ByteArrayOutputStream( );
            try {
                outputStream.write(searchImage);
                outputStream.write(dataValue);
            }
            catch(Exception e ){
                Toast.makeText(ControlPanel.this,"Can't add byte",Toast.LENGTH_LONG).show();

            }
            counterSearchImage +=1;
            searchImage = outputStream.toByteArray( );
            if(counterSearchImage == 309) {
                FileOutputStream myOutput = createDataFile();
                Bitmap myBitmap = BitmapFactory.decodeByteArray(searchImage, 0, searchImage.length);
                try {
                    myBitmap.compress(Bitmap.CompressFormat.JPEG, 85, myOutput);
                    myOutput.close();
                    Toast.makeText(ControlPanel.this,"Image received",Toast.LENGTH_LONG).show();
                } catch (Exception e) {
                    Toast.makeText(ControlPanel.this, "Can't write in file", Toast.LENGTH_LONG).show();
                }
                searchImage = new byte[0];
                counterSearchImage = 0;
            }
        }

    }

    private FileOutputStream createDataFile(){

        String search_path;
        String file_name_search = new SimpleDateFormat("yyyy-MM-dd_HH-mm-ss").format(Calendar.getInstance().getTime());

        // If there is external and writable storage
        if(Environment.MEDIA_MOUNTED.equals(Environment.getExternalStorageState()) && !Environment.MEDIA_MOUNTED_READ_ONLY.equals(Environment.getExternalStorageState())) {
            try {
                search_path = Environment.getExternalStorageDirectory().getPath() + "/Android/data/DriverAppData/" + file_name_search+".jpg";
                File searchFile = new File(search_path);
                searchFile.createNewFile(); // create new file if it does not already exists

                FileOutputStream output_search = new FileOutputStream(searchFile);
                Log.v("FILE", "File created");

                return output_search;

            } catch (IOException e) {
                return null;
            }

        } else {
            Toast.makeText(ControlPanel.this,"No ext storage",Toast.LENGTH_LONG).show();
            return null;
        }

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
            if (joystick_angle <= 20 || joystick_angle > 340)
                joystickCurrentValue = Constants.RIGHT;
            else if (joystick_angle <= 200 && joystick_angle > 155)
                joystickCurrentValue = Constants.LEFT;
            else if (joystick_angle <= 65 && joystick_angle > 20){
                if(!emergencyFront) {
                    joystickCurrentValue = Constants.FRONT + "&" + Constants.RIGHT;
                }
            }
            else if (joystick_angle <= 110 && joystick_angle > 65){
                if(!emergencyFront) {
                    joystickCurrentValue = Constants.FRONT;
                }
            }
            else if (joystick_angle <= 155 && joystick_angle > 110){
                if(!emergencyFront) {
                    joystickCurrentValue = Constants.FRONT + "&" + Constants.LEFT;
                }
            }

            else if (joystick_angle <= 245 && joystick_angle > 200){
                if(!emergencyBack) {
                    joystickCurrentValue = Constants.BACK+"&"+Constants.LEFT;
                }
            }
            else if (joystick_angle <= 290 && joystick_angle > 245){
                if(!emergencyBack) {
                    joystickCurrentValue = Constants.BACK;
                }
            }
            else if (joystick_angle <= 335 && joystick_angle > 290){
                if(!emergencyBack) {
                    joystickCurrentValue = Constants.BACK+"&"+Constants.RIGHT;
                }
            }
            if (joystickCurrentValue.equals(""))
                joystickCurrentValue = Constants.NOTHING;
        } else {
            joystickCurrentValue = Constants.NOTHING;
        }
        if(!joystickCurrentValue.equals(joystickValue)) {
            joystickValue = joystickCurrentValue;
            constructMessage(Constants.JOYSTIC, joystickCurrentValue);
        }
    }

    private void sendMessage(String message){
        if (btGatt != null) {
            if (transmitterCharacteristic != null) {
                    transmitterCharacteristic.setValue(message);
                    transmitterCharacteristic.setWriteType(BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE);
                    btGatt.writeCharacteristic(transmitterCharacteristic);
            }
        }
    }
    private synchronized void constructMessage(String key,String value){
        String message = key + "$" + value;
        Collections.addAll(msgTosend, message,message,message);
        if (!isSendingMesg){
            isSendingMesg = true;
            sendMessage(message);
        }
    }
    private synchronized void removeMsgSent(){
        msgTosend.remove(0);
    }
    private synchronized void clearMsgSent(){
        msgTosend.clear();
    }

    private synchronized boolean ckeckRecvMsgList(){
        return msgTosend.size()!=0;
    }


}
