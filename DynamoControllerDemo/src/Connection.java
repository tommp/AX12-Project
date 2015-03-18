import objects.Response;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.ConnectException;
import java.net.HttpURLConnection;
import java.net.URL;

public class Connection {

    private String url;
    private String deviceID;

    public Connection(String url, String deviceName){
        this.url = url;

        deviceID = getDeviceID(sendGetMessage("device/" + deviceName, false));
    }

    public String sendPostMessage(String message){
        try {
            HttpURLConnection httpConnection = createPostConnection();
            httpConnection.setDoOutput(true);
            DataOutputStream outputStream = new DataOutputStream(httpConnection.getOutputStream());
            outputStream.writeBytes(message);
            outputStream.flush();
            outputStream.close();


            int responseCode = httpConnection.getResponseCode();
            String responseMessage = getResponseMessage(httpConnection);

            System.out.println("Sent post message: " + message);
            System.out.println("Response code: " + responseCode);
            System.out.println("Response message: " + responseMessage);

            return responseMessage;
        } catch (IOException e) {
            e.printStackTrace();
            return "";
        }
    }

    public String sendGetMessage(String param, boolean deviceSpecific){
        try {
            HttpURLConnection httpConnection = createGetConnection(param, deviceSpecific);


            int responseCode = 0;
            try {
                responseCode = httpConnection.getResponseCode();
            } catch (ConnectException e) {
                e.printStackTrace();
                System.out.println("Unable to connect to host - Exiting");
                System.exit(3);
            }

            System.out.println("Sent GET message: " + param);
            System.out.println("Response code: " + responseCode);

            String response = getResponseMessage(httpConnection);

            return response;
        } catch (IOException e) {
            e.printStackTrace();
            return "";
        }
    }

    private String getResponseMessage(HttpURLConnection httpConnection){

        StringBuffer response = null;
        try {
            BufferedReader in = new BufferedReader(
                    new InputStreamReader(httpConnection.getInputStream()));
            String inputLine;
            response = new StringBuffer();

            while ((inputLine = in.readLine()) != null) {
                response.append(inputLine);
            }
            in.close();
        } catch (IOException e) {
            e.printStackTrace();
        }

        //print result
        System.out.println("Response message: " + response.toString());
        return  response.toString();
    }

    private HttpURLConnection createPostConnection() throws IOException{
        URL obj = new URL(url + "/device/" + deviceID);
        HttpURLConnection httpConnection = (HttpURLConnection) obj.openConnection();

        httpConnection.setRequestMethod("POST");
        httpConnection.setRequestProperty("User-Agent", "Mozilla/5.0");
        httpConnection.setRequestProperty("Accept-Language", "en-US,en;q=0.5");
        httpConnection.setRequestProperty("Content-Type", "application/json");
        return httpConnection;
    }

    private HttpURLConnection createGetConnection(String param, boolean deviceSpecific) throws IOException{
        URL obj;
        if(deviceSpecific)
            obj = new URL(url + "/" + deviceID + "/" + param);
        else
            obj = new URL(url + "/" + param);

        HttpURLConnection httpConnection = (HttpURLConnection) obj.openConnection();

        httpConnection.setRequestMethod("GET");
        httpConnection.setRequestProperty("User-Agent", "Mozilla/5.0");
        httpConnection.setRequestProperty("Accept-Language", "en-US,en;q=0.5");
        //httpConnection.setRequestProperty("Content-Type", "application/json");
        return httpConnection;
    }

    private String getDeviceID(String message){
        Response response = (Response) JSONConverter.fromJson(message, Response.class);

        if(response.getStatus().equals("error")) {
            System.out.println(response.getMessage());
            System.out.println("Unable to get the device id");
            System.exit(3);
        }
        return response.getMessage();
    }
}
