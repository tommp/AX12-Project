import jgamepad.Controller;
import jgamepad.enums.Analog;
import jgamepad.enums.Button;
import jgamepad.interfaces.ButtonPressedEvent;
import jgamepad.listeners.ButtonPressedListener;

public class CarDemo {

    private static final String URL = "http://78.91.7.89:9002";
    private static final String DEVICE_NAME = "Ruls";

    private static int RIGHT_ANALOG_MAX_VALUE = 24078;
    private static int LEFT_ANALOG_MAX_VALUE = 24918;

    private static int lastRightAnalogValue;
    private static int carId = 0;

    public static void main(String[] args){
        Connection connection = new Connection(URL, DEVICE_NAME);
        Controller.dllPath = System.getProperty("user.dir") + "\\libs";
        Controller controller = new Controller(0, 50);

        String responseString = connection.sendPostMessage(createCarMessage(0,1,2,3));

        Response response = (Response) JSONConverter.fromJson(responseString, Response.class);

        if(response.getStatus().equals("success"))
            carId = Integer.parseInt(response.getMessage());

        controller.addButtonListener(new ButtonPressedListener(Button.A, new ButtonPressedEvent() {
            @Override
            public void run(boolean pressed) {
                if(pressed){
                    System.out.println("Turning off");
                    String message = generateMoveCarMessage(0, 0);
                    connection.sendPostMessage(message);
                }
            }
        }));

        controller.addButtonListener(new ButtonPressedListener(Button.B, new ButtonPressedEvent() {
            @Override
            public void run(boolean pressed) {
                if(pressed){
                    System.out.println("Turning off");
                    String message = generateMoveCarMessage(50, 0);
                    connection.sendPostMessage(message);
                }
            }
        }));

        while(true){
            try {
                int rightAnalogValue = controller.getAnalogValue(Analog.rightStickY);
                if(rightAnalogValue != 0 || lastRightAnalogValue != 0) {
                    lastRightAnalogValue = rightAnalogValue;
                    int speed = getPercentage(rightAnalogValue, RIGHT_ANALOG_MAX_VALUE);
                    int direction = getPercentage(controller.getAnalogValue(Analog.leftStickX), LEFT_ANALOG_MAX_VALUE);

                    String message = generateMoveCarMessage(speed, direction);
                    connection.sendPostMessage(message);
                }
                Thread.sleep(50);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    private static int getPercentage(int analogValue, int max){
        double speed = (double) analogValue / max * 100;
        return (int) speed;
    }

    private static String generateMoveCarMessage(int speed, int direction){
        String moveMessage = "{ \"action\": \"moveCar\"," +
                "\"id\": " + carId + ", \"speed\": " + speed + ", \"direction\": " + direction + "}";

        return moveMessage;
    }

    private static String createCarMessage(int topLeft, int topRight, int bottomLeft, int bottomRight){
        Car car = new Car(topLeft, topRight, bottomLeft, bottomRight);

        return JSONConverter.toJson(car);
    }
}
