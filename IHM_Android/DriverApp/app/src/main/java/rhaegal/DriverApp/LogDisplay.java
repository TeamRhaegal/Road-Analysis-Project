package rhaegal.DriverApp;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Bundle;
import android.os.Environment;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ImageView;
import android.widget.Spinner;

import java.io.File;
import java.util.ArrayList;
import java.util.List;

public class LogDisplay extends AppCompatActivity implements AdapterView.OnItemSelectedListener {
    private Spinner fileSpinner;
    private ImageView viewSearchResult;
    private File rootFile;
    private String rootPath = Environment.getExternalStorageDirectory().getPath() + "/Android/data/DriverAppData";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.search_log);

        rootFile = new File( rootPath);
        fileSpinner = findViewById(R.id.file_spinner);
        viewSearchResult = findViewById(R.id.image_search_result);

        loadFileName();
        fileSpinner.setOnItemSelectedListener(this);
    }

    private void loadFileName(){
        List<String> list = new ArrayList<>();
        if (!Environment.MEDIA_MOUNTED.equals(Environment.getExternalStorageState())) {
            list.add("You don't have access to the files");
        }
        else{
            File[] searchFiles = rootFile.listFiles();
            if (searchFiles.length > 0) {
                for (File f : searchFiles) {
                    String fileName = f.getName();
                    list.add(fileName.substring(0, fileName.lastIndexOf(".")));
                }
            }
            else{
                list.add("You don't have any result saved");
            }

        }
        ArrayAdapter<String> dataAdapter = new ArrayAdapter<>(this,
                android.R.layout.simple_spinner_item, list);
        dataAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        fileSpinner.setAdapter(dataAdapter);
    }

    @Override
    public void onItemSelected(AdapterView<?> parent, View view,
                               int pos, long id) {
        File selectedFile = new File(rootPath + "/"+parent.getItemAtPosition(pos).toString()+".jpg");
        Bitmap myBitmap = BitmapFactory.decodeFile(selectedFile.getAbsolutePath());
        viewSearchResult.setImageBitmap(myBitmap);
    }

    @Override
    public void onNothingSelected(AdapterView<?> parent) {
        viewSearchResult.setImageResource(android.R.color.transparent);
    }

}
