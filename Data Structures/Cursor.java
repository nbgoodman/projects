package editor;

import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.event.ActionEvent;
import javafx.event.EventHandler;
import javafx.scene.paint.Color;
import javafx.scene.shape.Rectangle;
import javafx.scene.text.Text;
import javafx.util.Duration;

public class Cursor {
    public Rectangle cursor;
    public Cursor() {
        cursor = new Rectangle(1, 15);
        cursor.setX(5);
        cursor.setY(0);
    }
    private class RectangleBlinkEventHandler implements EventHandler<ActionEvent> {
        private int currentColorIndex = 0;
        private Color[] boxColors = {Color.TRANSPARENT, Color.BLACK};

        RectangleBlinkEventHandler() {
            // Set the color to be the first color in the list.
            changeColor();
        }
        private void changeColor() {
            cursor.setFill(boxColors[currentColorIndex]);
            currentColorIndex = (currentColorIndex + 1) % boxColors.length;
        }
        @Override
        public void handle(ActionEvent event) {
            changeColor();
        }
    }
    public void ChangeCursor(LinkedListText.Node maybe, int identify, double y_pos) {
        // Handles graphical cursor changes
        Text prevStuff = (Text) maybe.prev.item;
        Text cursorStuff = (Text) maybe.item;
        Text nextStuff = (Text) maybe.next.item;
        int cursor_height = (int) Math.round(1.21533203125*Editor.fontSizes);
        if (cursorStuff.getText().equals("")) {
            cursor.setY(0);
            cursor.setX(5);
        }
        else if (cursorStuff.getText().equals("\r")) {
            int something_x = (int) cursorStuff.getX();
            int something_y = (int) cursorStuff.getY();
            cursor.setX(something_x);
            cursor.setY(something_y);
        }
        else if (cursorStuff.getY() < nextStuff.getY() && identify == 1) {
            if (y_pos >= nextStuff.getY()) {
                cursor.setX(nextStuff.getX());
                cursor.setY(nextStuff.getY());
            }
            else {
                cursor.setX(cursorStuff.getX() + Math.round(cursorStuff.getLayoutBounds().getWidth()));
                cursor.setY(cursorStuff.getY());
            }
        }
        else if (cursorStuff.getY() < nextStuff.getY() && identify == 0 && !nextStuff.getText().equals("")  && !nextStuff.getText().equals("\r")) {
            cursor.setX(5);
            cursor.setY(nextStuff.getY());
        }
        else {
            int something_x = (int) (cursorStuff.getX() + Math.round(cursorStuff.getLayoutBounds().getWidth()));
            int something_y = (int) cursorStuff.getY();
            cursor.setX(something_x);
            cursor.setY(something_y);
        }
        cursor.setHeight(cursor_height);
    }
    public static void cursorSnap() {
        // Called When Cursor is Outside Window
        double cursor_end = Editor.cursorText.cursor.getY() + TextLayoutEngine.fontHeight;
        if (Editor.cursorText.cursor.getY() < Editor.current_scroll_value) {
            Editor.scrollText.setValue(Editor.cursorText.cursor.getY());
        }
        else if ((cursor_end) > (Editor.newHeight + Editor.current_scroll_value)) {
            Editor.scrollText.setValue(cursor_end - Editor.newHeight);
        }
    }
    public void makeRectangleColorChange() {
        // Handles Rectangle Blinking
        final Timeline timeline = new Timeline();
        timeline.setCycleCount(Timeline.INDEFINITE);
        RectangleBlinkEventHandler cursorChange = new RectangleBlinkEventHandler();
        KeyFrame keyFrame = new KeyFrame(Duration.seconds(.5), cursorChange);
        timeline.getKeyFrames().add(keyFrame);
        timeline.play();
    }
}