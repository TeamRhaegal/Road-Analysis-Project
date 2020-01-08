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
import java.util.Calendar;
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
    private ImageView battery;
    private TextView speed;
    private ImageView imageSign;
    private TextView advSign;
    private Button logButton;

    //STOP sign
    private Toast signToast;
    private AlertDialog dialogEmergencyStop;
    private AlertDialog dialogSearchSign;
    private Boolean emergencyFront = false;
    private Boolean emergencyBack = false;

    private CountDownTimer timerNotif;
    private CountDownTimer timerDisconnect;
    private byte[] searchImage;
    private int counterSearchImage;

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
        turbo = findViewById(R.id.turbo);
        joystick = findViewById(R.id.joystick);
        battery = findViewById(R.id.battery);
        speed = findViewById(R.id.speed);
        logButton = findViewById(R.id.file);
        counterSearchImage = 0;

        LayoutInflater inflater = getLayoutInflater();
        View layoutSign = inflater.inflate(R.layout.sign_toast,
                (ViewGroup) findViewById(R.id.custom_toast_container));

        imageSign = layoutSign.findViewById(R.id.imageSign);
        advSign = layoutSign.findViewById(R.id.textSign);

        signToast = new Toast(getApplicationContext());
        signToast.setGravity(Gravity.TOP, 0, 0);
        signToast.setDuration(Toast.LENGTH_LONG);
        signToast.setView(layoutSign);

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
                .setIcon(R.drawable.search_sign)
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
        setTurboButton();
        setJoystick();
        setLogButton();

        speed.setText(R.string.speed);

        started = false;
        connected = false;
        autonomous = false;
        turboed = false;
        driving = false;
        joystickValue = Constants.NOTHING;

        timerNotif = new CountDownTimer(1000, 100) {

            public void onTick(long millisUntilFinished) {
                //Nothing
            }

            public void onFinish() {
                enableNotification(btGatt);
            }

        };
        timerDisconnect = new CountDownTimer(1000, 100) {

            public void onTick(long millisUntilFinished) {
                //Nothing
            }

            public void onFinish() {
                if (btGatt != null) {
                    btGatt.disconnect();
                }
            }

        };

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
                    sendMessage(Constants.CONNECTION,Constants.OFF);
                    timerDisconnect.start();
                    //Log.i(TAG, "disconnect\n");
                } else {
                    if (btGatt == null) {
                        connect.setText(R.string.connecting);
                        btGatt = btDevice.connectGatt(ControlPanel.this, false, gattCallback, TRANSPORT_LE);
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
                            turboed = false;
                            driving = false;
                            joystickValue = Constants.NOTHING;
                            resetSymbols();
                            //Log.i(TAG, "autonomous\n");
                            start.setText(R.string.start);
                            start.getBackground().setColorFilter(Color.parseColor(Constants.ice), PorterDuff.Mode.MULTIPLY);
                            turbo.getBackground().setColorFilter(Color.parseColor(Constants.ice), PorterDuff.Mode.MULTIPLY);
                            sendMessage(Constants.MODE, Constants.AUTONOMOUS);
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
                    // Loop through available Characteristics.
                    for (BluetoothGattCharacteristic gattCharacteristic : gattCharacteristics) {
                        uuid = gattCharacteristic.getUuid().toString();
                        //Log.i(TAG, uuid + "\n");
                        if (uuid.equals(Constants.uuidTransmitterCharacteristic)) {
                            transmitterCharacteristic = gattCharacteristic;
                            sendMessage(Constants.CONNECTION,Constants.ON);

                            //Log.i(TAG, "found state\n");
                        } else if (uuid.equals(Constants.uuidReceiverCharacteristic)) {
                            receiverCharacteristic = gattCharacteristic;
                            //Log.i(TAG, "found feedback\n");
                            timerNotif.start();
                        }
                    }
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

            StringTokenizer tokens = new StringTokenizer(data, "$");
            String key = tokens.nextToken();
            String value1 = tokens.nextToken();
            String value2 = "";
            try{
                value2 = tokens.nextToken();}
            catch(Exception e){

            }

            switch (key) {
                case Constants.MODE :
                    changeMode(value1);
                    break;
                case Constants.BATTERY :
                    changeBatt(value1);
                    break;
                case Constants.SPEED:
                    changeSpeed(value1);
                    break;
                case Constants.SIGN:
                    advertizeSign(value1);
                    break;
                case Constants.EMERGENCYSTOP:
                    advertizeEmergency(value1,value2);
                    break;
                case Constants.IMAGE:
                    getImage(value1.getBytes());
                case Constants.OBJECT:
                    objectFound(value1);

            }
        }
    };

    ////////////////////////////////////////////////////////////////////////////////
    //Bluetooth functions

    private void objectFound(final String sizeValue){
        if (sizeValue.equals(Constants.BIG)){
            runOnUiThread(new Runnable() {
                              public void run() {
            Toast.makeText(ControlPanel.this,"Found a big object",Toast.LENGTH_LONG).show();}});
        }
        else if (sizeValue.equals(Constants.MEDIUM)){
            runOnUiThread(new Runnable() {
                public void run() {
                    Toast.makeText(ControlPanel.this,"Found a medium object",Toast.LENGTH_LONG).show();}});

        }
        else{
            runOnUiThread(new Runnable() {
                public void run() {
                    Toast.makeText(ControlPanel.this,"Found a small object",Toast.LENGTH_LONG).show();}});

        }
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
            emergencyBack = false;
            emergencyFront = false;
            joystickValue = Constants.NOTHING;
            runOnUiThread(new Runnable() {
                public void run() {
                    auto.getBackground().setColorFilter(Color.parseColor(Constants.ice), PorterDuff.Mode.MULTIPLY);
                    start.getBackground().setColorFilter(Color.parseColor(Constants.ice), PorterDuff.Mode.MULTIPLY);
                    turbo.getBackground().setColorFilter(Color.parseColor(Constants.ice), PorterDuff.Mode.MULTIPLY);
                    start.setText(R.string.start);
                    auto.setText(R.string.manual);
                    connect.setText(R.string.connect);
                    String conSpeedString = 0.0 + " km/h";
                    speed.setText(conSpeedString);
                    battery.setImageResource(R.drawable.ic_batt_full);
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
            UUID uuid = UUID.fromString("00002902-0000-1000-8000-00805f9b34fb");
            BluetoothGattDescriptor descriptor = characteristic.getDescriptor(uuid);

            if(descriptor!=null) {
                descriptor.setValue(BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE);
                if (!gatt.writeDescriptor(descriptor)) {
                    Toast.makeText(ControlPanel.this, "succeed write descriptor", Toast.LENGTH_LONG).show();
                }
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
                    sendMessage(Constants.MODE,Constants.AUTONOMOUS);

                } else if (modeValue.equals(Constants.ASSISTED)) {
                    if(autonomous) {
                        auto.setText(R.string.manual);
                        autonomous = false;
                    }
                    else{
                        if (started){
                            if(turboed){
                                sendMessage(Constants.TURBO,Constants.OFF);
                            }
                            sendMessage(Constants.JOYSTIC,Constants.NOTHING);
                        }
                    }
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
     * Function updating speed indicator in hm/h according to vehicle speed
     *
     * @param speedValue vehicle speed in m/s
     */
    private void changeSpeed(String speedValue) {
        double speedValueDb = Double.valueOf(speedValue);
        if(speedValueDb!=0){
            java.text.DecimalFormat df = new java.text.DecimalFormat("##.##");
            double convSpeedValue = speedValueDb *(3.6);
            final String conSpeedString = df.format(convSpeedValue) + " km/h";

            runOnUiThread(new Runnable() {
                public void run() {
                    speed.setText(conSpeedString);
                }
            });
        }
        else{
            runOnUiThread(new Runnable() {
                public void run() {
                    speed.setText(R.string.speed);
                }
            });
        }
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


    private void advertizeSign(final String signValue){
        if (signValue.equals(Constants.STOP)){
            advSign.setText(R.string.advStop);
            imageSign.setImageResource(R.drawable.stop_sign);
            signToast.show();
        }
        if (signValue.equals(Constants.SEARCH)){
            if(autonomous) {
                advSign.setText(R.string.advSearch);
                imageSign.setImageResource(R.drawable.search_sign);
                signToast.show();
            }
            else{
                runOnUiThread(new Runnable() {
                    public void run() {
                        dialogSearchSign.show();
                    }
                });
            }
        }
    }

    private void advertizeEmergency(final String areaValue,final String stateValue){
        if (areaValue.equals(Constants.FRONT)){
            if (stateValue.equals(Constants.ON)){
                emergencyFront = true;
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
            else if (stateValue.equals(Constants.OFF)){
                emergencyFront = false;

            }
        }
        else if (areaValue.equals(Constants.REAR)){
            if(!autonomous) {
                if (stateValue.equals(Constants.ON)) {
                    emergencyBack = true;

                } else if (stateValue.equals(Constants.OFF)) {
                    emergencyBack = false;

                }
            }
        }
    }

    private void getImage(final byte[] dataValue){
        if (counterSearchImage < 100){
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
            if(counterSearchImage == 100) {
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

        String search_path = null;
        String file_name_search = new SimpleDateFormat("yyyyMMdd_HHmmss").format(Calendar.getInstance().getTime());

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
                if(emergencyFront) {
                    dialogEmergencyStop.setMessage(getString(R.string.emergencyMsgFront));
                    runOnUiThread(new Runnable() {
                        public void run() {
                            dialogEmergencyStop.show();
                        }
                    });
                }
                else {
                    joystickCurrentValue = Constants.FRONT + "&" + Constants.RIGHT;
                }
            }
            else if (joystick_angle <= 110 && joystick_angle > 65){
                if(emergencyFront) {
                    dialogEmergencyStop.setMessage(getString(R.string.emergencyMsgFront));
                    runOnUiThread(new Runnable() {
                        public void run() {
                            dialogEmergencyStop.show();
                        }
                    });
                }
                else {
                    joystickCurrentValue = Constants.FRONT;
                }
            }
            else if (joystick_angle <= 155 && joystick_angle > 110){
                if(emergencyFront) {
                    dialogEmergencyStop.setMessage(getString(R.string.emergencyMsgFront));
                    runOnUiThread(new Runnable() {
                        public void run() {
                            dialogEmergencyStop.show();
                        }
                    });
                }
                else {
                    joystickCurrentValue = Constants.FRONT + "&" + Constants.LEFT;
                }
            }

            else if (joystick_angle <= 245 && joystick_angle > 200){
                if(emergencyBack) {
                    dialogEmergencyStop.setMessage(getString(R.string.emergencyMsgBack));
                    runOnUiThread(new Runnable() {
                        public void run() {
                            dialogEmergencyStop.show();
                        }
                    });
                }
                else {
                    joystickCurrentValue = Constants.BACK+"&"+Constants.LEFT;
                }
            }
            else if (joystick_angle <= 290 && joystick_angle > 245){
                if(emergencyBack) {
                    dialogEmergencyStop.setMessage(getString(R.string.emergencyMsgBack));
                    runOnUiThread(new Runnable() {
                        public void run() {
                            dialogEmergencyStop.show();
                        }
                    });
                }
                else {
                    joystickCurrentValue = Constants.BACK;
                }
            }
            else if (joystick_angle <= 335 && joystick_angle > 290){
                if(emergencyBack) {
                    dialogEmergencyStop.setMessage(getString(R.string.emergencyMsgBack));
                    runOnUiThread(new Runnable() {
                        public void run() {
                            dialogEmergencyStop.show();
                        }
                    });
                }
                else {
                    joystickCurrentValue = Constants.BACK+"&"+Constants.RIGHT;
                }
            }
            if (joystickCurrentValue.equals(""))
                joystickCurrentValue = Constants.NOTHING;
        } else {
            joystickCurrentValue = Constants.NOTHING;
        }
        if (!joystickCurrentValue.equals(joystickValue)){
            joystickValue = joystickCurrentValue;
            sendMessage(Constants.JOYSTIC, joystickCurrentValue);
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
