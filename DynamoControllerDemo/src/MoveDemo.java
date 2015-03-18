import jgamepad.Controller;
import jgamepad.enums.Analog;
import jgamepad.enums.Button;
import jgamepad.interfaces.ButtonPressedEvent;
import jgamepad.listeners.ButtonPressedListener;
import objects.Action;
import objects.Actuator;

public class MoveDemo {

    private static String URL = "http://78.91.7.89:9002";
    private static String DEVICE_NAME = "Ruls";

    private static int ANALOG_MAX_VALUE = 24078;

    private static int lastAnalogValue;

    public static void main(String[] args){
        Connection connection = new Connection(URL, DEVICE_NAME);
        Controller.dllPath = System.getProperty("user.dir") + "\\libs";
        Controller controller = new Controller(0, 50);

        controller.addButtonListener(new ButtonPressedListener(Button.A, new ButtonPressedEvent() {
            @Override
            public void run(boolean pressed) {
                if(pressed){
                    System.out.println("Turning off");
                    String message = generateMoveMessage(0);
                    connection.sendPostMessage(message);
                }
            }
        }));

        controller.addButtonListener(new ButtonPressedListener(Button.B, new ButtonPressedEvent() {
            @Override
            public void run(boolean pressed) {
                if(pressed){
                    System.out.println("Turning off");
                    String message = generateMoveMessage(50);
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
                    String message = generateMoveMessage(speed);
                    connection.sendPostMessage(message);
                }
                Thread.sleep(50);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    private static int getSpeed(int analogValue){
        double speed = (double) analogValue / ANALOG_MAX_VALUE * 100;
        return (int) speed;
    }

    private static String generateMoveMessage(int speed){
//        String moveMessage = "{ \"action\": \"move\"," +
//                "\"actuators\": [" +
//                "{\"id\":4, \"direction\":" + "\"" + direction + "\"" + ", \"speed\":" + speed + "}," +
//                "{\"id\":2, \"direction\":" + "\"" + direction + "\"" + ", \"speed\":" + speed + "}" +
//                "]}";

        Actuator actuator1 = new Actuator(2, speed);
        Actuator actuator2 = new Actuator(4, speed);

        Action action = new Action("move", new Actuator[] {actuator1, actuator2});

        return JSONConverter.toJson(action);
    }
}
