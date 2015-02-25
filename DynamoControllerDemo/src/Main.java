import jgamepad.Controller;
import jgamepad.enums.Analog;
import jgamepad.enums.Button;
import jgamepad.interfaces.ButtonPressedEvent;
import jgamepad.listeners.ButtonPressedListener;

public class Main {

    private static String URL = "http://vsop.online.ntnu.no:8080";

    private static int ANALOG_MAX_VALUE = 24078;

    private static int lastAnalogValue;

    public static void main(String[] args){
        Connection connection = new Connection(URL);
        Controller.dllPath = System.getProperty("user.dir") + "\\libs";
        Controller controller = new Controller(0, 50);

        controller.addButtonListener(new ButtonPressedListener(Button.A, new ButtonPressedEvent() {
            @Override
            public void run(boolean pressed) {
                if(pressed){
                    System.out.println("Turning off");
                    String message = generateMoveMessage(0, "clockwise");
                    connection.sendPostMessage(message);
                }
            }
        }));

        controller.addButtonListener(new ButtonPressedListener(Button.B, new ButtonPressedEvent() {
            @Override
            public void run(boolean pressed) {
                if(pressed){
                    System.out.println("Turning off");
                    String message = generateMoveMessage(50, "clockwise");
                    connection.sendPostMessage(message);
                }
            }
        }));

        while(true){
            try {
                int analogValue = controller.getAnalogValue(Analog.rightStickY);
                if(analogValue != 0 || lastAnalogValue != 0) {
                    lastAnalogValue = analogValue;
                    int speed = getSpeed(analogValue);
                    System.out.println("Speed: " + speed);
                    String message = generateMoveMessage(speed, analogValue < 0 ? "counterclockwise" : "clockwise");
                    connection.sendPostMessage(message);
                }
                Thread.sleep(50);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    private static int getSpeed(int analogValue){
        if(analogValue < 0)
            analogValue *= -1;
        double speed = (double) analogValue / ANALOG_MAX_VALUE * 100;
        return (int) speed;
    }

    private static String generateMoveMessage(int speed, String direction){
        String moveMessage = "{ \"action\": \"move\"," +
                "\"actuators\": [" +
                "{\"id\":4, \"direction\":" + "\"" + direction + "\"" + ", \"speed\":" + speed + "}," +
                "{\"id\":2, \"direction\":" + "\"" + direction + "\"" + ", \"speed\":" + speed + "}" +
                "]}";

        return moveMessage;
    }
}
