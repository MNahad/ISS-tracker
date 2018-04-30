void setup()
{
  Serial.begin(9600);
  pinMode(3, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(9, OUTPUT);
}

void loop()
{
  if(Serial.available())
  {
    runLED(Serial.read() - '0');
  }
  delay(500);
}

void runLED(int flag)
{
  switch (flag)
  {
    case 0:    //Slow sequence
      for (int count = 1; count <= 5; count++)
       {
         playTone(500, 50);
         for(int fade = 10; fade <= 250; fade += 10)
         {
           analogWrite(3, fade);
           analogWrite(6, fade);
           delay(40);
         }
         for(int fade = 250; fade >= 10; fade -= 10)
         {
           analogWrite(3, fade);
           analogWrite(6, fade);
           delay(40);
         }
       }
      digitalWrite(3, LOW);
      digitalWrite(6, LOW);
      break;
    case 1:    //Fast sequence
      for (int count = 1; count <= 10; count++)
      {
         playTone(250, 50);
         digitalWrite(3, HIGH);
         digitalWrite(6, HIGH);
         delay(500);
         digitalWrite(3, LOW);
         digitalWrite(6, LOW);
         delay(500);
      }        
      break;
    case 2:    //Max sequence
      for (int counter = 1; counter <= 5; counter++)
      {
        playTone(125, 50);
        for (int count = 1; count <= 10; count++)
        {
           digitalWrite(3, HIGH);
           delay(25);
           digitalWrite(3, LOW);
           delay(25);
           digitalWrite(6, HIGH);
           delay(25);
           digitalWrite(6, LOW);
           delay(25);
        }
      }
      break;
  }
}

void playTone(int gap, int duration)
{
  for (long i = 0; i < duration * 1000L; i += gap * 2)
  {
    digitalWrite(9, HIGH);
    delayMicroseconds(gap);
    digitalWrite(9, LOW);
    delayMicroseconds(gap);
  }
}
