import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class Connection {

    private String url;
    private String deviceID;

    public Connection(String url, String deviceName){
        this.url = url;

        deviceID = getDeviceID(sendGetMessage("device/" + deviceName, false));
    }

    public int sendPostMessage(String message){
        try {
            HttpURLConnection httpConnection = createPostConnection();
            httpConnection.setDoOutput(true);
            DataOutputStream outputStream = new DataOutputStream(httpConnection.getOutputStream());
            outputStream.writeBytes(message);
            outputStream.flush();
            outputStream.close();

            //httpConnection.setDoOutput(false);

            int responseCode = httpConnection.getResponseCode();

            System.out.println("Sent post message: " + message);
            System.out.println("Response code: " + responseCode);
            System.out.println("Response message: " + getResponseMessage(httpConnection));

            return responseCode;
        } catch (IOException e) {
            e.printStackTrace();
            return -1;
        }
    }

    public String sendGetMessage(String param, boolean deviceSpecific){
        try {
            HttpURLConnection httpConnection = createGetConnection(param, deviceSpecific);
            //httpConnection.setDoOutput(true);

            int responseCode = httpConnection.getResponseCode();

            System.out.println("Sent GET message: " + param);
            System.out.println("Response code: " + responseCode);

            String response = getResponseMessage(httpConnection);

            System.out.println("Response message: " + response);

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
        URL obj = new URL(url + "/" + deviceID);
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
        //TODO parse json
        System.out.println(message);
        return message;
    }
}
