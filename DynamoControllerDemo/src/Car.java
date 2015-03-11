
public class Car {

    private String create = "car";
    private int[] actuators = new int[4];

    public Car(int topLeft, int topRight, int bottomLeft, int bottomRight) {
        actuators[0] = topLeft;
        actuators[1] = topRight;
        actuators[2] = bottomLeft;
        actuators[3] = bottomRight;
    }

    public String toString(){
        return create;
    }
}
