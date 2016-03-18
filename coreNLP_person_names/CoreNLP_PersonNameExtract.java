import org.apache.tika.exception.TikaException;
import org.apache.tika.io.IOUtils;
import org.apache.tika.metadata.Metadata;
import org.apache.tika.parser.AutoDetectParser;
import org.apache.tika.parser.ner.corenlp.CoreNLPNERecogniser;
import org.apache.tika.sax.BodyContentHandler;
import org.json.JSONArray;
import org.json.JSONObject;
import org.xml.sax.ContentHandler;
import org.xml.sax.SAXException;

import java.io.*;
import java.util.Map;
import java.util.Set;

public class CoreNLP_PersonNameExtract {


    public static String parseToPlainText(String input_dir,String fileName) throws IOException, SAXException, TikaException {
        String file = input_dir + "/" + fileName;
        BodyContentHandler handler = new BodyContentHandler();
        AutoDetectParser parser = new AutoDetectParser();
        Metadata metadata = new Metadata();
        try (InputStream stream = new FileInputStream(file)) {
            parser.parse(stream, handler, metadata);
            return handler.toString();
        }
    }

    public static void fetchNames(String input_dir,String output_dir,String fileName, JSONObject result) {
        try {
            String text = parseToPlainText(input_dir, fileName);
            CoreNLPNERecogniser ner = new CoreNLPNERecogniser();
            Map<String, Set<String>> names = ner.recognise(text);
            if(names != null)
            {
                JSONArray persons = new JSONArray(names.get("PERSON"));
                //System.out.println(persons.toString(2));
                result.put(fileName, persons);
            }
            //JSONObject jNames = new JSONObject(names);
            //JSONArray personNames = jNames.getJSONArray("PERSON");
            //System.out.println(personNames.toString(2));
            //System.out.println(jNames.toString(2));
        }catch(Exception e)
        {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        String input_dir = args[0];
        String output_dir = args[1];
        File folder = new File(input_dir);
        File[] listOfFiles = folder.listFiles();
        JSONObject result = new JSONObject();
        for (int i = 0; i < listOfFiles.length; i++) {
            if (listOfFiles[i].isFile()) {
                System.out.println("fetchNames for File " + listOfFiles[i].getName());
                fetchNames(input_dir, output_dir, listOfFiles[i].getName(), result);
            } else if (listOfFiles[i].isDirectory()) {
                System.out.println("Skipping Directory " + listOfFiles[i].getName());
            }
        }
        //System.out.println(result.toString(2));
        try{
            String jsonFilePath = output_dir + "/" + "result.json";
            FileWriter fWrite = new FileWriter(jsonFilePath);
            fWrite.write(result.toString(2));
            fWrite.flush();
            fWrite.close();
        }catch(Exception e)
        {
            e.printStackTrace();
        }
    }
}
