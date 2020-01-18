package rhaegal.DriverApp;

import android.Manifest;
import android.app.AlertDialog;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothManager;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanResult;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.PorterDuff;
import android.graphics.Typeface;
import android.location.LocationManager;
import android.os.AsyncTask;
import android.os.Environment;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;
import android.widget.Toast;

import java.io.File;
import java.util.ArrayList;


public class scan extends AppCompatActivity {

    private final static String TAG = ControlPanel.class.getSimpleName();


    //variables
    Button scanningButton;
    TableLayout list;
    boolean scanning;

    LocationManager gpsManager;

    BluetoothManager btManager;
    BluetoothAdapter btAdapter;
    BluetoothLeScanner btScanner;

    private ArrayList deviceList = new ArrayList();

    private final static int REQUEST_BLUETOOTH = 1;
    private static final int PERMISSION_REQUEST_COARSE_LOCATION = 1;
    private static final int REQUEST_WRITE_STORAGE = 3;
    private int i = 0;
    ////////////////////////////////--------------------------////////////////////////


    //Initialisation method
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.scan);

        btManager = (BluetoothManager) getSystemService(Context.BLUETOOTH_SERVICE);
        btAdapter = btManager.getAdapter();

        gpsManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);


        // Ensures Bluetooth is available on the device and it is enabled. If not,
        // displays a dialog requesting user permission to enable Bluetooth.
        if (btAdapter == null) {
            final AlertDialog.Builder builder = new AlertDialog.Builder(this);
            builder.setTitle("Not compatible");
            builder.setMessage("Your phone does not support Bluetooth");
            builder.setPositiveButton("Exit", new DialogInterface.OnClickListener() {
                public void onClick(DialogInterface dialog, int which) {
                    System.exit(0);
                }
            });
            builder.setIcon(android.R.drawable.ic_dialog_alert);
            builder.show();
        }

        // Ensures coarse location permission is granted. If not displays a dialog requesting
        // user to grant permission.
        if (this.checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            final AlertDialog.Builder builder = new AlertDialog.Builder(this);
            builder.setTitle("This app needs location access");
            builder.setMessage("Please grant location access so this app can detect peripherals.");
            builder.setPositiveButton(android.R.string.ok, null);
            builder.setOnDismissListener(new DialogInterface.OnDismissListener() {
                @Override
                public void onDismiss(DialogInterface dialog) {
                    requestPermissions(new String[]{Manifest.permission.ACCESS_COARSE_LOCATION}, PERMISSION_REQUEST_COARSE_LOCATION);
                }
            });
            builder.show();
        }
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE}, REQUEST_WRITE_STORAGE);
        }

        // Ensures coarse location is enabled on the device. If not displays a dialog requesting
        // user to enable coarse location.
        if (!gpsManager.isProviderEnabled(LocationManager.GPS_PROVIDER)) {
            AlertDialog.Builder builder = new AlertDialog.Builder(this);
            builder.setMessage("Please enable gps so this app can detect peripherals.")
                    .setCancelable(false)
                    .setPositiveButton("Yes", new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog, int id) {
                            Intent intent = new Intent(android.provider.Settings.ACTION_LOCATION_SOURCE_SETTINGS);
                            startActivity(intent);
                        }
                    })
                    .setNegativeButton("No", new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog, int id) {
                            dialog.cancel();
                        }
                    });
            AlertDialog alert = builder.create();
            alert.show();
        }

        String path = Environment.getExternalStorageDirectory().getPath() + "/Android/data/DriverAppData/";
        File FileDir= new File(path);
        if (!FileDir.exists()) {
            FileDir.mkdir();
        }


        ////////////////////////////////--------------------------////////////////////////
        //identifying layout elements
        list = findViewById(R.id.list);
        scanningButton = findViewById(R.id.scanButton);

        //initializing buttons
        scanning = false;
        scanningButton.setText(R.string.scan);
        scanningButton.getBackground().setColorFilter(Color.parseColor(Constants.night), PorterDuff.Mode.MULTIPLY);


        btScanner = btAdapter.getBluetoothLeScanner();
        //scan button
        scanningButton.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                if (scanning) {
                    stopScanning();
                }else {
                    startScanning();
                }
            }
        });


    }

    ////////////////////////////////-------location permission------////////////////////////
    @Override
    public void onRequestPermissionsResult(int requestCode, String permissions[], int[] grantResults) {
        switch (requestCode) {
            case PERMISSION_REQUEST_COARSE_LOCATION: {
                if (grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    final AlertDialog.Builder builder = new AlertDialog.Builder(this);
                    builder.setTitle("Full functionality");
                    builder.setMessage("coarse location permission granted");
                    builder.setPositiveButton(android.R.string.ok, null);
                    builder.show();
                } else {
                    final AlertDialog.Builder builder = new AlertDialog.Builder(this);
                    builder.setTitle("Limited functionality");
                    builder.setMessage("Since location access has not been granted, this app will not be able to discover beacons.");
                    builder.setPositiveButton(android.R.string.ok, null);
                    builder.show();
                }
            }
        }
    }

    @Override
    protected void onStart() {
        super.onStart();
        Log.i(TAG, "Start\n");
    }

    @Override
    protected void onResume() {
        super.onResume();
        Log.i(TAG, "Resume\n");

        if (!btAdapter.isEnabled()) {
            Intent enable = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivityForResult(enable, REQUEST_BLUETOOTH);
        }
        btScanner = btAdapter.getBluetoothLeScanner();
    }

    @Override
    protected void onPause() {
        super.onPause();
        Log.i(TAG, "Pause\n");
    }

    @Override
    protected void onStop() {
        super.onStop();
        Log.i(TAG, "Stop\n");
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        Log.i(TAG, "Close\n");
    }

    ////////////////////////////////-------Scanning------////////////////////////

    //scanning method
    public void startScanning() {
        AsyncTask.execute(new Runnable() {
            @Override
            public void run() {
                if(btScanner != null){
                    btScanner.startScan(leScanCallback);
                } else {
                    Log.i(TAG, "No scanner\n");
                }

            }
        });
        scanning = true;
        scanningButton.setText(R.string.stop);
    }

    //stop scanning method
    public void stopScanning() {
        AsyncTask.execute(new Runnable() {
            @Override
            public void run() {
                if(btScanner != null){
                    btScanner.stopScan(leScanCallback);
                } else {
                    Log.i(TAG, "No scanner\n");
                }
            }
        });
        scanning = false;
        scanningButton.setText(R.string.scan);
    }

    // Device scan callback.
    private ScanCallback leScanCallback = new ScanCallback() {
        @Override
        public void onScanResult(int callbackType, ScanResult result) {

            final BluetoothDevice btDevice = result.getDevice();
            final String deviceName = btDevice.getName();
            final String deviceAddress = btDevice.getName();

            if (deviceName != null && deviceName.length() > 0 && !deviceList.contains(deviceAddress)) {
                deviceList.add(deviceAddress);
                AddDevice(btDevice);
            }
        }
    };

    // Device scan callback.
    public void AddDevice(final BluetoothDevice btDevice) {

        final String deviceName = btDevice.getName();
        final String deviceAddress = btDevice.getAddress();

        TableRow tRow = new TableRow(scan.this);
        LinearLayout lView = new LinearLayout(scan.this);
        lView.setOrientation(LinearLayout.VERTICAL);

        TextView Text = new TextView(scan.this);
        Text.setTextColor(Color.BLACK);
        Text.setTypeface(null, Typeface.BOLD);
        Text.setText(deviceName);

        TextView Text2 = new TextView(scan.this);
        Text2.setTextColor(Color.BLACK);
        Text2.setText(deviceAddress);

        final Button button = new Button(scan.this);
        button.setId(i);
        i++;
        button.setText(R.string.choose);
        button.setTextColor(Color.parseColor(Constants.white));
        button.getBackground().setColorFilter(Color.parseColor(Constants.blue), PorterDuff.Mode.MULTIPLY);
        button.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                stopScanning();
                //access to the Control page
                final Intent intent = new Intent(scan.this, ControlPanel.class);
                intent.putExtra(Constants.EXTRAS_DEVICE_ADDRESS, deviceAddress);
                startActivity(intent);
            }
        });

        lView.addView(Text);
        lView.addView(Text2);
        tRow.addView(lView);
        tRow.addView(button);

        list.addView(tRow, new TableLayout.LayoutParams(TableRow.LayoutParams.MATCH_PARENT, TableRow.LayoutParams.WRAP_CONTENT));
    }


}
