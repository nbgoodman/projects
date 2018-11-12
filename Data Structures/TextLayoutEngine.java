package editor;

import java.util.ArrayList;
import java.util.LinkedList;
import javafx.geometry.VPos;
import javafx.scene.text.Font;
import javafx.scene.text.Text;

public class TextLayoutEngine {
    LinkedListText<Text> letters;
    LinkedListText.Node pointer;
    public ArrayList<LinkedListText.Node> ys;
    public static LinkedList<LinkedListText.Node> undo = new LinkedList<>();
    public static LinkedList<LinkedListText.Node> redo = new LinkedList<>();
    public TextLayoutEngine() {
        Text a = new Text(5, 0, "");
        a.setFont(Font.font(Editor.fontNames, Editor.fontSizes));
        letters = new LinkedListText<>(a);
        pointer = letters.getSentinel();
    }
    private int current_x;
    private int current_y;
    public static double fontHeight;
    public editor.LinkedListText.Node space_watch;

    public void addCharacter(String a, int identity) {
        //Adds character to letters
        Text current = new Text(0, 0, a);
        current.setTextOrigin(VPos.TOP);
        current.setFont(Font.font(Editor.fontNames, Editor.fontSizes));
        pointer.addNode(current);
        pointer = pointer.next;
        if (identity != 0) {
            addToUndo(pointer);
        }
        Editor.textroot.getChildren().add(current);
    }

    public void removeCharacter(int identity) {
        // Removes character from letters
        Text temp = (Text) pointer.item;
        if (temp.getText().equals("")) {
        }
        else if (identity == 0){
            pointer = pointer.prev;
            Text removedText = (Text) pointer.removeNode();
            Editor.textroot.getChildren().remove(removedText);
        }
        else {
            addToUndo(pointer);
            pointer = pointer.prev;
            Text removedText = (Text) pointer.removeNode();
            removedText.setStrikethrough(true);
            Editor.textroot.getChildren().remove(removedText);
        }
    }
    public void render() {
        // renders graphical representation
        current_x = 5;
        current_y = 0;
        space_watch = null;
        ys = new ArrayList<>();
        LinkedListText.Node start = letters.getSentinel();
        start = start.next;
        Text want_size = (Text) start.item;
        want_size.setFont(Font.font("Verdana", Editor.fontSizes));
        fontHeight = Math.round(1.21533203125*Editor.fontSizes);
        ys.add(start);
        while (start != letters.getSentinel()) {
            Text current = (Text) start.item;
            String newline = "\r";
            String space = " ";
            if (space.equals(current.getText())) {
                space_watch = start;
            }
            current.setFont(Font.font("Verdana", Editor.fontSizes));
            if (newline.equals(current.getText())) {
                new_line(start);
            }
            x_change(current);
            start = start.next;
            if (current_x > Editor.newWidth) {
                if (space_watch == null) {
                    new_line(start);
                }
                else {
                    Text charSpace = (Text) space_watch.item;
                    if (space.equals(current.getText())) {
                    }
                    else if (charSpace.getY() == current_y) {
                        WordWrap(space_watch.next, start);
                    }
                    else {
                        new_line(start);
                    }
                    }
                }
            }
        scrollCheck();
    }
    public void WordWrap (LinkedListText.Node t, LinkedListText.Node start) {
        // Called when backtracking and word wrapping is needed
        new_line(t);
        while (t != start) {
            Text curr = (Text) t.item;
            x_change(curr);
            t = t.next;
        }
    }
    public void scrollCheck() {
        // Checks if all text is in the window
        int last_index = ys.size() - 1;
        LinkedListText.Node last_start = ys.get(last_index);
        Text last_line = (Text) last_start.item;
        int text_height = (int) Math.round((last_line.getY() + fontHeight) - Editor.newHeight);
        Editor.scrollText.setMax(Math.max(text_height, 0));
        if (Editor.scrollText.getMax() < Editor.scrollText.getValue()) {
            Editor.scrollText.setValue(Editor.scrollText.getMax());
        }
    }

    public void x_change(Text curr) {
        // Changes current_x so new letter will be after
        curr.setX(current_x);
        curr.setY(current_y);
        double x = curr.getLayoutBounds().getWidth();
        int x_change = (int) Math.round(x);
        current_x += x_change;
    }


    public void new_line(LinkedListText.Node start) {
        // handles creating new lines and updating current_x and current_y
        ys.add(start);
        Text temp = (Text) start.item;
        int y_change = (int) Math.round(1.21533203125*Editor.fontSizes);
        current_y += y_change;
        current_x = 5;
        temp.setY(current_y);
        temp.setX(current_x);
    }

    public void CursorUp(double x_pos, double y_pos) {
        // handles edge cases for cursor up
        int everything_Height = (int) Math.round(1.21533203125*Editor.fontSizes);
        int index = (int) (y_pos/everything_Height);
        if (ys.size() <= 1 || index == 0) {
        }
        else {
            index-=1;
            LinkedListText.Node searching = ys.get(index);
            if (index != 0) {
                searching = searching.next;
            }
            CursorStuff(searching, x_pos, index * everything_Height);
        }
    }
    public void CursorDown(double x_pos, double y_pos) {
        // handles edge cases for cursor down
        int everything_Height = (int) Math.round(1.21533203125*Editor.fontSizes);
        int index = (int) (y_pos/everything_Height);
        if (ys.size() <= 1 || index == ys.size()-1) {
        }
        else {
            index+=1;
            LinkedListText.Node searching = ys.get(index);
            searching = searching.next;
            CursorStuff(searching, x_pos, index * everything_Height);
        }

    }
    public void CursorClick(double click_x, double click_y) {
        // handles edge cases when mouse clicking
        int everything_Height = (int) Math.round(1.21533203125 * Editor.fontSizes);
        int index = (int) click_y / everything_Height;
        int realindex = Math.min(ys.size() - 1, index);
        LinkedListText.Node searching = ys.get(realindex);
        searching = searching.next;
        CursorStuff(searching, click_x, realindex*everything_Height);
    }
    public void CursorStuff(LinkedListText.Node searching, double click_x, double click_y) {
        // handles finding closest letter in a line
        Text stuff = (Text) searching.item;
        if (stuff.getText().equals("")) {
        }
        else {
            while (!stuff.getText().equals("\r") && stuff.getY() == click_y) {
                if (click_x <= stuff.getX()) {
                    Text next_text = (Text) searching.next.item;
                    Text prev_text = (Text) searching.prev.item;
                    double prev_distance = click_x - prev_text.getX();
                    double first_distance = click_x - stuff.getX();
                    double next_distance = next_text.getX() - click_x;
                    if (Math.abs(next_distance) < Math.abs(first_distance) && !next_text.getText().equals("") && next_text.getY() == click_y) {
                        searching = searching.next;
                    }
                    else if (Math.abs(prev_distance) < Math.abs(first_distance) && !prev_text.getText().equals("") && prev_text.getY() == click_y) {
                        searching = searching.prev;
                    }
                    break;
                }
                searching = searching.next;
                stuff = (Text) searching.item;
                if (stuff.getText().equals("")) {
                    break;
                }
            }
        }
        pointer = searching.prev;
    }
    public void CursorRight() {
        // handles moving cursor to right
        Text temp = (Text) pointer.next.item;
        if (temp.getText().equals("")) {
        }
        else {
            pointer = pointer.next;
        }
    }
    public void CursorLeft() {
        // handles moving cursor to left
        Text temp = (Text) pointer.item;
        if (temp.getText().equals("")) {
        }
        else {
            pointer = pointer.prev;
        }
    }
    public void addToUndo (LinkedListText.Node a) {
        // adds recent action to undo
        if (undo.size() < 100) {
            undo.addLast(a);
        }
        else {
            undo.addLast(a);
            undo.remove();
        }
    }
    public void Undo() {
        // handles undoing. Also appends to redo.
        if (undo.isEmpty()) {
        }
        else {
            LinkedListText.Node temp = undo.removeLast();
            Text text = (Text) temp.item;
            if (text.isStrikethrough()) {
                text.setStrikethrough(false);
                pointer = temp.prev;
                pointer.reAddNode(temp);
                pointer = pointer.next;
                Editor.textroot.getChildren().add(text);
                redo.addLast(temp);
            }
            else {
                text.setStrikethrough(true);
                pointer = temp;
                this.removeCharacter(0);
                redo.addLast(temp);
            }
        }
    }
    public void Redo() {
        // handles redo.  Also appends to undo.
        if (redo.isEmpty()) {
        }
        else {
            LinkedListText.Node temp = redo.removeLast();
            Text text = (Text) temp.item;
            if (text.isStrikethrough()) {
                text.setStrikethrough(false);
                pointer = temp.prev;
                pointer.reAddNode(temp);
                pointer = pointer.next;
                Editor.textroot.getChildren().add(text);
                undo.addLast(temp);
            }
            else {
                text.setStrikethrough(true);
                pointer = temp;
                this.removeCharacter(0);
                undo.addLast(temp);
            }
        }
    }
}