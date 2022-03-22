#include <libgpsmm.h>
#include <iostream>
#include <unistd.h>
using namespace std;

class NEO7M
{
    public:
        gpsmm gps_rec;

        NEO7M() : gps_rec{"localhost", "2947"} {};

        double * position()
        {
            struct gps_data_t* last;
            static double pos[3];

            last = poll();
            pos[0] = last->fix.latitude;
            pos[1] = last->fix.longitude;
            pos[2] = last->fix.altitude; // Maybe replace with altHAE or altMSL since this is being deprecated
        
            return pos;
        }

        struct gps_data_t* poll()
        {
            if ((gps_rec.read()) == nullptr) {
                gps_data_t* err = 0;
                std::cerr << "GPSD read error.\n";
                return err;
            }

            return gps_rec.read();
        }
};

int main()
{
    NEO7M gps = NEO7M();

    while(true)
    {
        cout << gps.position()[0];
    }
}

