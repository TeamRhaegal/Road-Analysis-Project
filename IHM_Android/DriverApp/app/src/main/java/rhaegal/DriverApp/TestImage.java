package rhaegal.DriverApp;


import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.os.Environment;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.widget.ImageView;
import android.widget.Toast;

import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Calendar;

public class TestImage extends AppCompatActivity {
    String rootPath = Environment.getExternalStorageDirectory().getPath() + "/Android/data/DriverAppData/myImage.txt";
    File rootFile;
    private ImageView viewSearchResult;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.search_log);

        rootFile = new File( rootPath);
        viewSearchResult = findViewById(R.id.image_search_result);
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        byte[] stBytes = new byte[0];
        try {
            BufferedReader br = new BufferedReader(new FileReader(rootFile));


            String st;
            while ((st = br.readLine()) != null){
                stBytes = st.getBytes();
                outputStream.write(stBytes);}

        }catch(Exception e){
            Toast.makeText(TestImage.this,"Can't read",Toast.LENGTH_LONG).show();
        }

        FileOutputStream myOutput = createDataFile();
        byte[] myImage = outputStream.toByteArray();

        Bitmap myBitmap = BitmapFactory.decodeByteArray(stBytes, 0, stBytes.length);
        createJpg(myBitmap,myOutput);

        File selectedFile = new File(Environment.getExternalStorageDirectory().getPath() + "/Android/data/DriverAppData/testImage.jpg");

        Bitmap myBitmap2 = BitmapFactory.decodeFile(selectedFile.getAbsolutePath());
        viewSearchResult.setImageBitmap(myBitmap2);

    }

    private void createJpg(Bitmap myBitmap, FileOutputStream myOutput){
        try {
            myBitmap.compress(Bitmap.CompressFormat.JPEG, 85, myOutput);
            myOutput.close();
            Toast.makeText(TestImage.this,"Image received",Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            Toast.makeText(TestImage.this, "Can't write in file", Toast.LENGTH_LONG).show();
        }

    }

    private FileOutputStream createDataFile(){

        String search_path = null;
        String file_name_search = new SimpleDateFormat("yyyyMMdd_HHmmss").format(Calendar.getInstance().getTime());

        // If there is external and writable storage
        if(Environment.MEDIA_MOUNTED.equals(Environment.getExternalStorageState()) && !Environment.MEDIA_MOUNTED_READ_ONLY.equals(Environment.getExternalStorageState())) {
            try {
                search_path = Environment.getExternalStorageDirectory().getPath() + "/Android/data/DriverAppData/" + "testImage.jpg";
                File searchFile = new File(search_path);
                searchFile.createNewFile(); // create new file if it does not already exists

                FileOutputStream output_search = new FileOutputStream(searchFile);
                Log.v("FILE", "File created");

                return output_search;

            } catch (IOException e) {
                return null;
            }

        } else {
            Toast.makeText(TestImage.this,"No ext storage",Toast.LENGTH_LONG).show();
            return null;
        }

    }
}
