/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package beamserver;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import javax.sound.sampled.Clip;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.UnsupportedAudioFileException;
import javax.sound.sampled.LineUnavailableException;
import javax.sound.sampled.AudioInputStream;
import java.io.File;
import java.sql.Timestamp;
import java.util.Date;

/**
 *
 * @author Sergio
 */
public class BeamServer {
    
     public static int nDevices; //Denota el número de dispositivos que se van a conectar.
     
     public static int PORT; //Es el puerto inicial al que se conectan la primera vez todos los clientes.
     
     public static ServerSocket server; //Socket inicial del servidor (channel server). Con este se proporcionará al cliente el puerto final de conexión.
     
     public static Socket[] iniClients; //Sockets correspondientes al número de clientes. Hace referencia a la primera conexión.
     
     public static int[] availablePorts; //Lista de puertos disponibles para la conexión. Será una lista de 10 puertos en total, pudiendo abarcar 10 clientes.
     
     public static boolean[] takenPorts; //Array booleana que indica qué puerto de la lista está libre (False) y cuál está ocupado (True).
     
     public static Socket firstConnection; //Socket del cliente relacionado con el puerto inicial común (PORT). Será común para todos los dispositivos.
     
     public static ServerSocket finalServer; //Socket del servidor correspondiente al PUERTO FIJO del cliente
     
     public static String[] timeStamp; //Marcas de tiempo del servidor cuando recibe cada ACK
     
     
    
    public static void main(String[] args) throws InterruptedException, IOException { //Los parámetros los determinamos en Rum->Set Project Configuration
        
        nDevices = Integer.parseInt(args[0]); //Pasamos el número de dispositivos de 'string' a entero.
        iniClients = new Socket[nDevices]; //Clientes de la primera conexión, que se corresponde con el número de dispositivos.
        timeStamp = new String[nDevices];
        PORT = 5000;
        
        //ESTO SE PUEDE PONER COMO UNA FUNCIÓN
        availablePorts = new int[10];
        for(int i = 0; i < 10; i++){ //Rellenamos los 10 puertos disponibles a partir del valor del puerto inicial
            availablePorts[i] = PORT + i + 1;
        }
        
        takenPorts = new boolean[10];
        
        try{
            server = new ServerSocket(PORT);
            System.out.println("Server started");
            
            int nClients = 0;
            while(nClients < nDevices){ //Mientras el número de conexiones no supere al número de dispositivos, el servidor espera la entrada de nuevos clientes.
                firstConnection = server.accept(); //Espera hasta que se produce la conexión.
                System.out.println("First connection accepted");
                int finalPort = Search4port(takenPorts); //Asignamos un puerto libre de la lista de los 10 puertos disponibles.
                takenPorts[nClients] = true; //Marcamos como ocupado el puerto que está en uso.
                System.out.println("Port " + finalPort);
                
                finalServer = new ServerSocket(finalPort);
                DataOutputStream communication = new DataOutputStream(firstConnection.getOutputStream()); //Stream que comunica el servidor con el cliente.
                communication.writeInt(finalPort); //Se le pasa al cliente el puerto fijo de conexión.
                iniClients[nClients] = finalServer.accept(); //Espera hasta que se produzca la segunda conexión.
                System.out.println("Client " + (nClients + 1 ) + " accepted at port "+ finalPort);
                
                communication.close(); //Cerramos comunicación.
                firstConnection.close(); //Cerramos el socket correspondiente al cliente. Ese cliente está operado.
                nClients++; //Incrementamos el número de clientes
            }
            
        }catch (IOException ex) {
            System.out.println(ex);
        }
        
        Recording(iniClients);
        
        getTimeStamp(iniClients);
        //timeView(timeStamp);
        //playChirp(iniClients);
        delay();
        stopRecording(iniClients);
        getTimeStamp(iniClients);
        saveFiles(iniClients);
        
        
        
    }
    
    //----------------------------------------------------------------------------------------------------------------------------
    //----------------------------------------------------FUNCTIONS---------------------------------------------------------------
    //----------------------------------------------------------------------------------------------------------------------------
    
    //Función que tiene de argumentos de entrada el vector booleano correspondiente a los puertos ocupados
    //y devuelve qué puerto de la lista de puertos disponibles está libre para la conexión.
    static public int Search4port(boolean[] takenPorts){
        int j = 0;
        int freePort = PORT;
        boolean out = true; //Variable de salida del bucle
        while(j < 10 && out){
           if(takenPorts[j] == false){// SE PUEDE PONER COMO !takenPorts[j]. Si el puerto está libre...
               freePort = availablePorts[j];
               out = false;
           }
           j++;
        }
        return freePort;
    }
    
    
    
    static public void Recording(Socket[] Clients){

        int nConnections = 0;
        
        //Espero a que CADA UNO de los clientes esté listo para grabar.
        System.out.println("Ready to Record");
        try{
        while(nConnections < nDevices){
            DataInputStream input = new DataInputStream(Clients[nConnections].getInputStream());
            while(!input.readUTF().equals("READY")){ //Si no se recibe esta 'keyword', no se continuará con el procedimiento.
                
            }
            nConnections++;
        }
        }catch(IOException e){};
        
        try
        {
            Thread.sleep(2000);
        }catch(InterruptedException e){}
        
        //Se manda grabar a todos los clientes conectados.
        for (int i = 0; i < nDevices; i++){
            try{
                DataOutputStream  output = new DataOutputStream(Clients[i].getOutputStream());
                DataInputStream ACK = new DataInputStream(Clients[i].getInputStream());
        
                System.out.println("Recording");
                output.writeUTF("START"); //Se envía la 'keyword' correspondiente a la aplicación para que comience la grabación.
                while(!ACK.readUTF().equals("OK")){}
            }catch(IOException e){};
            
            timeStamp[i] = Time();
        
        }
        serverImpulse();
        
    }
    
    //Función que introduce el delay correspondiente a la duración de la grabación
    static public void delay()
    {
        try
        {
            //Thread.sleep(12000);
            Thread.sleep(190000);
        }catch(InterruptedException e){}
    }
    
    
    //Envía la orden de parar la grabación a cada cliente
    static public void stopRecording(Socket[] Clients) throws InterruptedException{
        
        for (int i = 0 ;i < nDevices; i++){
            try{
            DataOutputStream  output = new DataOutputStream(Clients[i].getOutputStream());
            output.writeUTF("STOP");
            }
            catch(IOException e){};
        }
    }
    
    //Función que guarda las grabaciones de cada móvil
    static public void saveFiles(Socket cliente[]) throws FileNotFoundException, IOException{
        
        for(int i = 0; i < nDevices; i++){
            
            String filename = "Device" + i + ".raw";
            System.out.println("File Opened " + (i + 1));
            int buf = 15050000;
            byte [] buffer = new byte[buf];
            
            FileOutputStream fos = new FileOutputStream(filename); //Se crea el archivo con el nombre correspondiente. Se destruye cualquier archivo con el mismo nombre.
            BufferedInputStream bis = new BufferedInputStream(cliente[i].getInputStream()); //Almacena el stream de datos procedente del cliente (grabación).
            BufferedOutputStream bos = new BufferedOutputStream(fos, buf); //Flujo de salida almacenado en un buffer
           
            int inputByte;
            boolean out = false;
            //int counter = 0;
            while (!out){ //Cuando out = true se sale del bucle
                //inputByte = bis.read();
                inputByte = bis.read(buffer, 0, buffer.length);
                if(inputByte != -1){ //El método read devuelve -1 cuando no quedan bytes por leer.
                    //bos.write(inputByte);
                    bos.write(buffer, 0, inputByte);
                    //System.out.println(inputByte);
                    //counter++;
                }
                else{ //Acabamos de escribir bytes y nos salimos del bucle
                    out = true;
                    //System.out.println(counter + " Bytes saved");
                }
            }
            
            
            bos.flush(); //Se vacía el buffer en el archivo creado.

            bos.close();
            bis.close();
            System.out.println("File " + (i + 1) + " Saved");

        }
    }
    
    //Función que lee la marca de tiempo procedente de cada móvil
    static public void getTimeStamp(Socket Clients[]){
        int nConnections = 0;
        try{
        while(nConnections < nDevices){
            DataInputStream input = new DataInputStream(Clients[nConnections].getInputStream());
            String ts = input.readUTF();
            System.out.println("Time Stamp " + (nConnections + 1) + ": " + ts);
            nConnections++;
            
        }
        }catch(IOException e){};
    }
    
    static public String Time(){
        Date date= new Date();
        long time = date.getTime();
        Timestamp ts1 = new Timestamp(time);
        String ts = ts1.toString();
        return ts;
    }
    
    static public void serverImpulse(){
        try{
            AudioInputStream audioInputStream = AudioSystem.getAudioInputStream(new File("tren_impulsos.wav").getAbsoluteFile());
            //AudioInputStream audioInputStream = AudioSystem.getAudioInputStream(new File("impulso.wav").getAbsoluteFile());
            Clip clip = AudioSystem.getClip();
            clip.open(audioInputStream);
            clip.start();
            System.out.println("Chirp en: " + Time());
        }catch(UnsupportedAudioFileException | IOException | LineUnavailableException ex){
            System.out.println("Error al reproducir el sonido.");}
    }
    
    //Función que manda a cada móvil la señal para que reproduzca el Chirp (cada 1.5 segundos)
    static public void playChirp(Socket Clients[]) throws InterruptedException{
        
        for (int i = 0; i < nDevices; i++){
            try{
                DataOutputStream  salida = new DataOutputStream(Clients[i].getOutputStream());
                salida.writeUTF("CHIRP");
                Thread.sleep(1000);
            }
        
            catch(IOException e){};
        }
    }
    
    static public void timeView(String timeStamp[]){
        for (int i = 0; i < nDevices; i++){
            System.out.println("ACK " + i + " en " + timeStamp[i]);
            
        }
    }
    
    
    
}


