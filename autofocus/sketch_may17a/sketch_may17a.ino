// z axis
int x1 = 13;
int x2 = 12;
int x3 = 11;
int x4 = 10;

// y axis 
int x5 = 9;
int x6 = 8;
int x7 = 7;
int x8 = 6;

// x axis 
int x9  = 5;
int x10 = 4;
int x11 = 3;
int x12 = 2;

int x1_tmp, x2_tmp, x3_tmp, x4_tmp;

int delaytime = 4;
int focusStep = 100;
String com; 
String axis;
String direction;


// functions///
void Step_A(int x1, int x2, int x3, int x4){
  digitalWrite(x1,HIGH);
  digitalWrite(x2,LOW);
  digitalWrite(x3,LOW);
  digitalWrite(x4,LOW);
}

void Step_B(int x1, int x2, int x3, int x4){
  digitalWrite(x1,LOW);
  digitalWrite(x2,HIGH);
  digitalWrite(x3,LOW);
  digitalWrite(x4,LOW);
}

void Step_C(int x1, int x2, int x3, int x4){
  digitalWrite(x1,LOW);
  digitalWrite(x2,LOW);
  digitalWrite(x3,HIGH);
  digitalWrite(x4,LOW);
}

void Step_D(int x1, int x2, int x3, int x4){
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
  digitalWrite(x5,LOW);
  digitalWrite(x6,LOW);
  digitalWrite(x7,LOW);
  digitalWrite(x8,LOW);
  digitalWrite(x9,LOW);
  digitalWrite(x10,LOW);
  digitalWrite(x11,LOW);
  digitalWrite(x12,LOW);
}
  
void forward (int x1, int x2, int x3, int x4){
  for(int i=0; i<focusStep; i++){
    Step_A(x1, x2, x3, x4);
    delay(delaytime);
    Step_B(x1, x2, x3, x4);
    delay(delaytime);
    Step_C(x1, x2, x3, x4);
    delay(delaytime);
    Step_D(x1, x2, x3, x4);
    delay(delaytime);
  }
}

 void backward(int x1, int x2, int x3, int x4){
  for(int i=0; i<focusStep; i++) {
    Step_D(x1, x2, x3, x4);
    delay(delaytime);
    Step_C(x1, x2, x3, x4);
    delay(delaytime);
    Step_B(x1, x2, x3, x4);
    delay(delaytime);
    Step_A(x1, x2, x3, x4);
    delay(delaytime);
  }
}


//end of functions
void setup () {
  pinMode (x1, OUTPUT);
  pinMode (x2, OUTPUT);
  pinMode (x3, OUTPUT);
  pinMode (x4, OUTPUT);
  pinMode (x5, OUTPUT);
  pinMode (x6, OUTPUT);
  pinMode (x7, OUTPUT);
  pinMode (x8, OUTPUT);
  pinMode (x9, OUTPUT);
  pinMode (x10, OUTPUT);
  pinMode (x11, OUTPUT);
  pinMode (x12, OUTPUT);
  Serial.begin(9600);
}

void loop () {
 if (Serial.available() > 0) {
   // read the incoming byte once: 
   // format : 
   // delay (2 chars) + " " + focusStep (4 chars) + " " +  axisdirection (3 chars : x/y/z + fw/bw)
   // Example :
   // 04 0100 zfw
   // NEED TO ADD 0 IN FRONT TO HAVE GOOD FORMAT
   com = Serial.readString();
   delaytime = com.substring(0, 2).toInt();
   focusStep = com.substring(3, 7).toInt();
   axis = com.substring(8, 9);
   direction = com.substring(9, 11);
   Serial.println(com);
   Serial.println(com.substring(0, 2));
   Serial.println(com.substring(3, 7));
   Serial.println(axis);
   Serial.println(direction);
  }

//movement ////////////////////////////////////////// 
  if (axis == "x" || axis == "y" || axis == "z") {
    Serial.println("z");
    x1_tmp = x1;
    x2_tmp = x2;
    x3_tmp = x3;
    x4_tmp = x4;
    if (axis == "y") {
      x1_tmp = x5;
      x2_tmp = x6;
      x3_tmp = x7;
      x4_tmp = x8;
    }
    if (axis == "x") {
      x1_tmp = x9;
      x2_tmp = x10;
      x3_tmp = x11;
      x4_tmp = x12;
    }

    if (direction == "fw") {
      Serial.println("fw");
      forward(x1_tmp, x2_tmp, x3_tmp, x4_tmp);
    }
    if (direction == "bw") {
      Serial.println("bw");
      backward(x1_tmp, x2_tmp, x3_tmp, x4_tmp);
    }
  }

///////////NULL//////////////
  Stop();
  axis = "";
  direction = "";
  com="";
}



