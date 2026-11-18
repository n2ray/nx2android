from pathlib import Path
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'nxnative/dm/android/java/org/nx2a/CarStatusLayout.java'

class CarStatusLayoutTest(unittest.TestCase):
    def test_status_stays_off_controls_and_screen_edges(self):
        code = '''package org.nx2a; public class Check {
 public static void main(String[] args) {
  float[] d=new float[5+3*9]; int menu=4+2*9;
  d[menu+1]=500; d[menu+2]=60; d[menu+3]=40; d[menu+4]=30;
  float[] p=CarStatusLayout.place(d,3,1000,500,120,30);
  if(p==null || p[0]<=540 || p[0]+120>1000) throw new AssertionError("right");
  d[5]=650; d[6]=60; d[7]=80; d[8]=40;
  p=CarStatusLayout.place(d,3,1000,500,120,30);
  if(p==null || p[0]+120>=460) throw new AssertionError("left");
  d[14]=350; d[15]=60; d[16]=80; d[17]=40;
  if(CarStatusLayout.place(d,3,1000,500,120,30)!=null) throw new AssertionError("overlap");
  if(CarStatusLayout.place(new float[4],3,1000,500,120,30)!=null) throw new AssertionError("invalid");
 }}'''
        with tempfile.TemporaryDirectory() as tmp:
            test=Path(tmp)/'Check.java'; test.write_text(code)
            subprocess.run(['javac','-d',tmp,str(SOURCE),str(test)],check=True)
            subprocess.run(['java','-cp',tmp,'org.nx2a.Check'],check=True)

if __name__ == '__main__': unittest.main()
