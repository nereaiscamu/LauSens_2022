int x1 = 13;
int x2 = 12;
int x3 = 11;
int x4 = 10;
int delaytime=2;
int focusStep = 100;
String com; 
String line1;
String line2;


// functions///


void Step_A(){
  digitalWrite(x1,HIGH);
  digitalWrite(x2,LOW);
  digitalWrite(x3,LOW);
  digitalWrite(x4,LOW);
  }
void Step_B(){
  digitalWrite(x1,LOW);
  digitalWrite(x2,HIGH);
  digitalWrite(x3,LOW);
  digitalWrite(x4,LOW);
  }
void Step_C(){
  digitalWrite(x1,LOW);
  digitalWrite(x2,LOW);
  digitalWrite(x3,HIGH);
  digitalWrite(x4,LOW);
  }
void Step_D(){
  digitalWrite(x1,LOW);
  digitalWrite(x2,LOW);
  digitalWrite(x3,LOW);
  digitalWrite(x4,HIGH);
  }

void Stop(){
  digitalWrite(x1,LOW);
  digitalWrite(x2,LOW);
  digitalWrite(x3,LOW);
  digitalWrite(x4,LOW);
}
  
void forward (){
  for(int i=0; i<focusStep; i++){
    Step_A();
    delay(delaytime);
    Step_B();
    delay(delaytime);
    Step_C();
    delay(delaytime);
    Step_D();
    delay(delaytime);
    }}
 void backward(){
  for(int i=0; i<focusStep; i++){
    Step_D();
    delay(delaytime);
    Step_C();
    delay(delaytime);
    Step_B();
    delay(delaytime);
    Step_A();
    delay(delaytime);
    }}


//end of functions


void setup (){
pinMode (x1, OUTPUT) ;
pinMode (x2, OUTPUT) ;
pinMode (x3, OUTPUT) ;
pinMode (x4, OUTPUT) ;
Serial.begin(9600);
}
void loop (){
 if (Serial.available() > 0) {
   // read the incoming byte once:
   com = Serial.readString();
   focusStep = com.toInt();
   Serial.println(com);

    // read the incoming byte once:
    com = Serial.readString();
    Serial.println(com);
    line1 = com.substring(0, 3);
    line2 = com.substring(3, 7);
    // Serial.println(line1);
    // Serial.println(line2);

  }
//time///////////////////////////////////////////
if(line2 == "150"){
  delaytime= 4;
  }
  if(line2 == "100"){
  delaytime= 8;
  }
  if(line2 == "050"){
  delaytime= 12;
  }
  if(line2 == "025"){
  delaytime= 14;
  }
//movement ////////////////////////////////////////// 
  if (line1=="xfw"){
    forward();

  }
  if (line1=="xbw"){
    backward();
  }

///////////NULL//////////////
  Stop();
  line1 = "";
  line2 = "";
  com="";
}



