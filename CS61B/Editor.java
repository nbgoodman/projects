package editor;

import javafx.application.Application;
import javafx.beans.value.ChangeListener;
import javafx.beans.value.ObservableValue;
import javafx.event.EventHandler;
import javafx.geometry.Orientation;
import javafx.scene.Group;
import javafx.scene.Scene;
import javafx.scene.input.KeyCode;
import javafx.scene.input.KeyEvent;
import javafx.scene.input.MouseEvent;
import javafx.scene.paint.Color;
import javafx.scene.text.Text;
import javafx.stage.Stage;
import javafx.scene.control.ScrollBar;
import java.util.LinkedList;

public class Editor extends Application {
    private static final int WINDOW_WIDTH = 500;
    private static final int WINDOW_HEIGHT = 500;
    public static int newHeight = 500;
    public static int current_scroll_value;
    public static int scrollBarWidth = 500;
    public TextLayoutEngine textList = new TextLayoutEngine();
    public static Cursor cursorText = new Cursor();
    public static ScrollBar scrollText;
    public static int newWidth = 495;
    public static Group textroot = new Group();
    public static int fontSizes = 12;
    public static String fontNames = "Verdana";
    public FileHolder stuff;

    /** An EventHandler to handle keys that get pressed. */
    private class KeyEventHandler implements EventHandler<KeyEvent> {
        KeyEventHandler(final Group root) {
            root.getChildren().add(textroot);
        }
        @Override
        public void handle(KeyEvent keyEvent) {
            if (keyEvent.getEventType() == KeyEvent.KEY_TYPED) {
                String characterTyped = keyEvent.getCharacter();
                if (keyEvent.isShortcutDown()) {
                    }
                else if (characterTyped.length() > 0 && characterTyped.charAt(0) != 8) {
                    textList.addCharacter(keyEvent.getCharacter(), 1);
                    textList.render();
                    Text check = (Text) textList.pointer.item;
                    if (check.getX() <= newWidth) {
                        Editor.cursorText.ChangeCursor(textList.pointer, 2, 0);
                    }
                    Cursor.cursorSnap();
                    TextLayoutEngine.redo = new LinkedList<>();
                    keyEvent.consume();
                }
                else if (characterTyped.charAt(0) == 8) {
                    textList.removeCharacter(1);
                    textList.render();
                    Text check = (Text) textList.pointer.item;
                    if (check.getX() <= newWidth) {
                        Editor.cursorText.ChangeCursor(textList.pointer, 0, 0);
                    }
                    Cursor.cursorSnap();
                    TextLayoutEngine.redo = new LinkedList<>();
                }
            }
            else if (keyEvent.getEventType() == KeyEvent.KEY_PRESSED) {
                KeyCode code = keyEvent.getCode();
                if (keyEvent.isShortcutDown()) {
                    if (code == KeyCode.P) {
                        int x = (int) cursorText.cursor.getX();
                        int y = (int) cursorText.cursor.getY();
                        System.out.println(x + ", " + y);
                        keyEvent.consume();
                    } else if (code == KeyCode.PLUS || code == KeyCode.EQUALS) {
                        fontSizes += 4;
                        textList.render();
                        Editor.cursorText.ChangeCursor(textList.pointer, 2, 0);
                    } else if (code == KeyCode.MINUS) {
                        fontSizes = Math.max(4, fontSizes - 4);
                        textList.render();
                        Editor.cursorText.ChangeCursor(textList.pointer, 2, 0);
                    } else if (code == KeyCode.S) {
                        stuff.SaveFile(textList);
                    } else if (code == KeyCode.Z) {
                        textList.Undo();
                        textList.render();
                        Editor.cursorText.ChangeCursor(textList.pointer, 2, 0);
                        Cursor.cursorSnap();
                    } else if (code == KeyCode.Y) {
                        textList.Redo();
                        textList.render();
                        Editor.cursorText.ChangeCursor(textList.pointer, 2, 0);
                        Cursor.cursorSnap();
                    }
                } else {
                    if (code == KeyCode.UP) {
                        Text a = (Text) textList.pointer.item;
                        Text b = (Text) textList.pointer.next.item;
                        if (a.getY() < b.getY() && !b.getText().equals("") && !b.getText().equals("\r")) {
                            textList.CursorUp (5, b.getY());
                            cursorText.ChangeCursor(textList.pointer, 0, 0);
                            }
                        else {
                            double x_pos = a.getX() + a.getLayoutBounds().getWidth();
                            textList.CursorUp(x_pos, a.getY());
                            Cursor.cursorSnap();
                            cursorText.ChangeCursor(textList.pointer, 0, 0);
                        }
                    } else if (code == KeyCode.DOWN) {
                        Text a = (Text) textList.pointer.item;
                        Text b = (Text) textList.pointer.next.item;
                        if (a.getY() < b.getY() && !b.getText().equals("") && !b.getText().equals("\r")) {
                            textList.CursorDown(5, b.getY());
                            cursorText.ChangeCursor(textList.pointer, 0, 0);
                            }
                        else {
                            double x_pos = a.getX() + a.getLayoutBounds().getWidth();
                            textList.CursorDown(x_pos, a.getY());
                            Cursor.cursorSnap();
                            cursorText.ChangeCursor(textList.pointer, 0, 0);
                        }
                    } else if (code == KeyCode.RIGHT) {
                        textList.CursorRight();
                        Cursor.cursorSnap();
                        cursorText.ChangeCursor(textList.pointer, 0, 0);
                    } else if (code == KeyCode.LEFT) {
                        textList.CursorLeft();
                        cursorText.ChangeCursor(textList.pointer, 0, 0);
                        Cursor.cursorSnap();
                    }
                }
            }
            }
        }
    public class MouseEventHandler implements EventHandler<MouseEvent> {
        MouseEventHandler(Group root) {
        }
        @Override
        public void handle(MouseEvent mouseEvent) {
            double mousePressedX = mouseEvent.getX();
            double mousePressedY = mouseEvent.getY() + scrollText.getValue();
            textList.CursorClick(mousePressedX, mousePressedY);
            cursorText.ChangeCursor(textList.pointer, 1, mousePressedY);
            Cursor.cursorSnap();
        }
    }
    private int getDimensionInsideMargin(int outsideDimension) {
        return outsideDimension - 5;
    }

    @Override
    public void start(Stage primaryStage) {
        Group root = new Group();
        Scene scene = new Scene(root, WINDOW_WIDTH, WINDOW_HEIGHT, Color.WHITE);
        Application.Parameters a = getParameters();
        stuff = new FileHolder(a);
        stuff.OpenFile(textList);
        scrollText = new ScrollBar();
        scrollText.setOrientation(Orientation.VERTICAL);
        scrollText.setMax(0);
        scrollText.setPrefHeight(newHeight);
        scrollText.setMin(0);
        scrollText.setValue(0);
        scrollText.setLayoutX(scrollBarWidth - scrollText.getLayoutBounds().getWidth());
        newWidth = 495 - (int) Math.round(scrollText.getLayoutBounds().getWidth());

        scene.widthProperty().addListener(new ChangeListener<Number>() {
            @Override
            public void changed(ObservableValue<? extends Number> observableValue, Number oldScreenWidth, Number newScreenWidth) {
                newWidth = getDimensionInsideMargin(newScreenWidth.intValue() - (int) Math.round(scrollText.getLayoutBounds().getWidth()));
                scrollBarWidth = Math.round(newScreenWidth.intValue());
                scrollText.setLayoutX(scrollBarWidth - (int) Math.round(scrollText.getLayoutBounds().getWidth()));
                textList.render();
                Editor.cursorText.ChangeCursor(textList.pointer, 2, 0);
            }
            });
        scene.heightProperty().addListener(new ChangeListener<Number>() {
            @Override
            public void changed(ObservableValue<? extends Number> observableValue, Number oldScreenHeight, Number newScreenHeight) {
                    newHeight = Math.round(newScreenHeight.intValue());
                    scrollText.setPrefHeight(newHeight);
                    textList.render();
                    Editor.cursorText.ChangeCursor(textList.pointer, 2, 0);
                }
            });

        scrollText.valueProperty().addListener(new ChangeListener<Number>() {
            public void changed(ObservableValue<? extends Number> observableValue, Number oldValue, Number newValue) {
                textroot.setLayoutY(-newValue.intValue());
                cursorText.cursor.setLayoutY(-newValue.intValue());
                textList.render();
                Editor.cursorText.ChangeCursor(textList.pointer, 2, 0);
                current_scroll_value = newValue.intValue();
            }
        });
        EventHandler<KeyEvent> keyEventHandler =
                new KeyEventHandler(root);
        EventHandler<MouseEvent> mouseEventHandler = new MouseEventHandler(root);
        scene.setOnKeyTyped(keyEventHandler);
        scene.setOnKeyPressed(keyEventHandler);
        scene.setOnMouseClicked(mouseEventHandler);
        root.getChildren().add(cursorText.cursor);
        root.getChildren().add(scrollText);
        cursorText.makeRectangleColorChange();
        textList.render();
        Editor.cursorText.ChangeCursor(textList.pointer, 2, 0);

        primaryStage.setTitle("Single Letter Display Simple");

        // This is boilerplate, necessary to setup the window where things are displayed.
        primaryStage.setScene(scene);
        primaryStage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}