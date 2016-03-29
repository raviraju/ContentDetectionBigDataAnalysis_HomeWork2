import org.apache.tika.metadata.Metadata;
import org.apache.tika.parser.ParseContext;
import org.apache.tika.parser.journal.JournalParser;
import org.apache.tika.sax.BodyContentHandler;
import org.xml.sax.ContentHandler;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;

import java.io.*;
import java.util.HashSet;
import java.util.Set;

public class TEI_MetaData {

    public static String cwd = System.getProperty("user.dir") + "/";

    public static Set<String> TeiKeys = new HashSet<String>();
    public static void initializeTeiKeys() {
        
        TeiKeys.add("grobid:header_Title");
        TeiKeys.add("grobid:header_Authors");
        //TeiKeys.add("grobid:header_TEIXMLSource");
        //TeiKeys.add("grobid:header_TEIJSONSource");
        TeiKeys.add("grobid:header_Keyword");
        TeiKeys.add("grobid:header_FullAffiliations");
        TeiKeys.add("grobid:header_Affiliation");
        TeiKeys.add("grobid:header_Address");
        TeiKeys.add("grobid:header_Class");
        
        TeiKeys.add("title");
        TeiKeys.add("dc:title");
        TeiKeys.add("dc:format");

        TeiKeys.add("mxmpTPg:NPages");
        TeiKeys.add("xmp:CreatorTool");
        TeiKeys.add("resourceName");
        TeiKeys.add("creator");
        TeiKeys.add("created");
        TeiKeys.add("Author");
        TeiKeys.add("meta:author");
        TeiKeys.add("Company");

        TeiKeys.add("Content-Length");
        TeiKeys.add("Content-Type");
        TeiKeys.add("Creation-Date");

        TeiKeys.add("date");
        TeiKeys.add("Last-Modified");
        TeiKeys.add("Last-Save-Date");
        TeiKeys.add("modified");
        TeiKeys.add("meta:creation-date");
        TeiKeys.add("meta:save-date");
        
    }

    @SuppressWarnings("unchecked")
    public static void putKeyValue_JsonObj(JSONObject json_obj, String key, String value){
        json_obj.put(key,value);
    }
    @SuppressWarnings("unchecked")
    public static void addJsonArray(JSONArray jsonArray, String obj){
        jsonArray.add(obj);
    }
    @SuppressWarnings("unchecked")
    public static void putKeyArray_JsonObj(JSONObject json_obj, String key, JSONArray jsonArray){
        json_obj.put(key,jsonArray);
    }

    public static void writeTEIJson(String fileName,String output_dir, Metadata metadata) throws IOException {

        JSONObject jsonObj = new JSONObject();

        //System.out.println(metadata.names());
        String[] names = metadata.names();
        System.out.println(names.length);
        for(int i = 0; i < names.length; ++i) {
            if(TeiKeys.contains(names[i])) {
				String key = names[i].replaceAll(":","__");				
                System.out.printf("Adding %-50s \n ", key);
                JSONArray jsonArray = new JSONArray();

                String[] values = metadata.getValues(names[i]);
                for(int j=0; j<values.length; ++j) {
                    addJsonArray(jsonArray, values[j]);
                }
                putKeyArray_JsonObj(jsonObj, key, jsonArray);
				
				String jsonFilePath = output_dir + "/" + fileName + ".json";
				FileWriter fWrite = new FileWriter(jsonFilePath);
				fWrite.write(jsonObj.toJSONString());
				//System.out.println(jsonObj.toJSONString());
				fWrite.flush();
				fWrite.close();
            }
        }
    }

    public static void fetchTEI(String input_dir,String output_dir,String fileName) {
        String file = input_dir + "/" + fileName;
        ContentHandler handler = new BodyContentHandler();
        Metadata metadata = new Metadata();
        InputStream stream = null;
        JournalParser jParser = new JournalParser();
        //CustomParser jParser = new CustomParser();

        try {
            stream = new FileInputStream(file);
            jParser.parse(stream, handler, metadata, new ParseContext());
            writeTEIJson(fileName, output_dir, metadata);

        }catch (IOException e){
            
            String errorFilePath = output_dir + "/errorFiles.txt";
            BufferedWriter bw = null;
			try {
				bw = new BufferedWriter(new FileWriter(errorFilePath, true));
				bw.write(fileName);
				bw.newLine();
				bw.flush();
			} catch (IOException ioe) {
				ioe.printStackTrace();
			} finally {
				if (bw != null) try {
					bw.close();
				} catch (IOException ioe2) {
					ioe2.printStackTrace();
				}
			}            
        }
        catch (Exception e){
            e.printStackTrace();
        }
    }

    public static void main(String[] args) throws Exception {

        initializeTeiKeys();

        String input_dir = args[0];
        String output_dir = args[1];
        File folder = new File(input_dir);
        File[] listOfFiles = folder.listFiles();

        for (int i = 0; i < listOfFiles.length; i++) {
            if (listOfFiles[i].isFile()) {
                System.out.println((i+1) + " : fetchTEI for File : " + listOfFiles[i].getName());
                fetchTEI(input_dir, output_dir, listOfFiles[i].getName());
            } else if (listOfFiles[i].isDirectory()) {
                System.out.println("Skipping Directory " + listOfFiles[i].getName());
            }
        }

    }
}




