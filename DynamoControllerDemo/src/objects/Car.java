package objects;

public class Car {

    private String action = "createCar";
    private int[] actuators = new int[2];

    public Car(int topLeft, int topRight, int bottomLeft, int bottomRight) {
        actuators[0] = topLeft;
        actuators[1] = topRight;
        //actuators[2] = bottomLeft;
        //actuators[3] = bottomRight;
    }

    public String toString(){
        return action;
    }
}
