#include <Stepper.h>
Stepper moteur_axe_x = Stepper(400,13,12,11,10); // On initialise les moteurs
Stepper moteur_axe_y = Stepper(400,5,4,3,2);

String data = "";
String posI = "";
String posJ = "";
int posX = 0;
int posY = 0;
char sep = ';'; 
boolean next = false;

void setup() {
  Serial.begin(115200);// On initialise le port série à 115200 afin d'avoir une plus grande vitesse de transmission d'information
  moteur_axe_x.setSpeed(40);// On initialise la vitesse des moteurs 
  moteur_axe_y.setSpeed(40);
}

void loop() {
  while(Serial.available()){// En premier on vérifie si il y a un envoi d'information de l'ordinateur
    char c = Serial.read();// On lit chaque caractère séparément puis on les ajoute à notre variable data, cette méthode est plus rapide que la méthode readString()
    data += c;
    delay(2);
  }  
  if(data != "" and data != "ERROR"){
    for(int i = 0; i < data.length(); i++){ // On lit ici notre texte
      if(!next){ // Si erreur on revient en position initiale
        if(data[i] == sep){ // Ici on lit les valeurs envoyées pour les séparer pour chaque moteur, le séparateur est un ";"
          next = true; // On incrémente chaque quantité de pas à faire pour chaque moteur avec chaque caractère
        }
        else{
          posI += data[i];
        }
      }
      else{
        posJ += data[i];
      }
    }
    motorsmooth(posI.toInt(), posJ.toInt());// On déplace les moteurs en accord avec les valeurs recue par l'ordinateur
    Serial.print("ok");// On renvoit un message pour signifier à l'ordinateur qu'il peut relancer une photo
    //positionInitiale(posI.toInt(), posJ.toInt()); // On met à jour la posistion initiale pour pouvoir revenir à la position initiale
    next = false;
    posI = "";
    posJ = "";
  }
  else if(data == "ERROR"){ // Ici on revient en position initiale
    //motorsmooth(-posX, -posY);
    //moteur_axe_x.step(-posX);
    //moteur_axe_y.step(-posY);
    posX = 0;
    posY = 0;
  }
  data = "";
}

void positionInitiale(int i, int j){ // Cette fonction a pour objectif de revenir en position initiale
  posX += i;
  posY += j;
}

void motorsmooth(int i, int j){ // Cette fonction déplace le système en ligne droite avec les moteurs en simultané
  int move2 = j*0.4; // On modifie le nombre de pas à effectuer pour chaque moteur. Ces valeurs sont arbitraires et ont été choisies en tatonnant
  int move1 = -i*0.8;
  positionInitiale(move1, move2);
  int countstep = 0;
  if (abs(move1)>abs(move2)){
    for (int i = 1; i<=abs(move1); i++){
      if (countstep/i<abs(move1)/abs(move2)){
        if (move2>0){
          moteur_axe_y.step(1);
          countstep++;
        }
        else{
          moteur_axe_y.step(-1);
          countstep++;
        }
      }
      if(move1>0){
        moteur_axe_x.step(1);
      }
      else{
        moteur_axe_x.step(-1);
      }
    }
  }
  else{
    for (int i = 1; i<=abs(move2); i++){
      if (countstep/i<abs(move2)/abs(move1)){
        if (move1>0){
          moteur_axe_x.step(1);
          countstep++;
        }
        else{
          moteur_axe_x.step(-1);
          countstep++;
        }
      }
      if(move2>0){
        moteur_axe_y.step(1);
      }
      else{
        moteur_axe_y.step(-1);
      }
    }
  }
}
