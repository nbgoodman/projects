package editor;

import javafx.application.Application;
import javafx.application.Platform;
import javafx.scene.text.Text;
import java.io.*;
import java.util.List;

public class FileHolder {
    Application.Parameters args;
    public static boolean debug = false;
    public File current_file;
    public FileHolder(Application.Parameters a) {
        args = a;
    }

    public void SaveFile(TextLayoutEngine textList) {
        // handles saving files
        try {
            FileWriter writer = new FileWriter(current_file, false);
            BufferedWriter bufferedwriter = new BufferedWriter(writer);
            LinkedListText.Node temp_pointer = textList.letters.getSentinel();
            temp_pointer = temp_pointer.next;
            while (temp_pointer != textList.letters.getSentinel()) {
                Text current = (Text) temp_pointer.item;
                if (current.equals("\r")) {
                    char a = '\n';
                    bufferedwriter.write(a);
                }
                else {
                    char a = current.getText().charAt(0);
                    bufferedwriter.write(a);
                }
                temp_pointer = temp_pointer.next;
            }
            textList.pointer = textList.letters.getSentinel();
            bufferedwriter.close();
        }
            catch(FileNotFoundException fileNotFoundException){
                System.out.println("File not found! Exception was: " + fileNotFoundException);
            }catch(IOException ioException){
                System.out.println("Error when copying; exception was: " + ioException);
            }
        }

    public void OpenFile(TextLayoutEngine textList) {
        // handles opening files
        List<String> inputs = args.getRaw();
        if (inputs.size() < 1) {
            System.out.println("You need to input a filename");
            Platform.exit();
        }
        else {
            try {
                if (inputs.size() == 2 && inputs.get(1).equals("debug")) {
                        debug = true;
                    }
                current_file = new File(inputs.get(0));
                if (current_file.isDirectory()) {
                    System.out.println("Unable to open " + inputs.get(0));
                    Platform.exit();
                }
                else if (current_file.exists()) {
                    FileReader reader = new FileReader(current_file);
                    BufferedReader bufferedreader = new BufferedReader(reader);
                    int intread;
                    while ((intread = bufferedreader.read()) != -1) {
                        char TextRead = (char) intread;
                        if (TextRead == '\n') {
                            textList.addCharacter("\r", 1);
                        }
                        else if (TextRead == '\r') {
                            textList.addCharacter("\r", 1);
                            bufferedreader.read();
                        }
                        else {
                            textList.addCharacter(String.valueOf(TextRead), 1);
                        }
                    }
                    textList.pointer = textList.letters.getSentinel();
                    bufferedreader.close();
                }
            } catch (FileNotFoundException fileNotFoundException) {
                System.out.println("File not found! Exception was: " + fileNotFoundException);
            } catch (IOException ioException) {
                System.out.println("Error when copying; exception was: " + ioException);
            }
        }
    }

    public static void print(String toPrint) {
        // handles if print should happen depending on if debug is there or not
        if (debug) {
            System.out.println(toPrint);
        }
    }
}