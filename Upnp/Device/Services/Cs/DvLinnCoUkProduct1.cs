using System;
using System.Runtime.InteropServices;
using System.Text;
using Zapp;

namespace Zapp
{
    public class DvProviderLinnCoUkProduct1 : DvProvider, IDisposable
    {
        [DllImport("DvLinnCoUkProduct1")]
        static extern uint DvProviderLinnCoUkProduct1Create(uint aDeviceHandle);
        [DllImport("DvLinnCoUkProduct1")]
        static extern void DvProviderLinnCoUkProduct1Destroy(uint aHandle);
        [DllImport("DvLinnCoUkProduct1")]
        static extern unsafe int DvProviderLinnCoUkProduct1SetPropertyRoom(uint aHandle, char* aValue, uint* aChanged);
        [DllImport("DvLinnCoUkProduct1")]
        static extern unsafe void DvProviderLinnCoUkProduct1GetPropertyRoom(uint aHandle, char** aValue);
        [DllImport("DvLinnCoUkProduct1")]
        static extern unsafe int DvProviderLinnCoUkProduct1SetPropertyStandby(uint aHandle, int aValue, uint* aChanged);
        [DllImport("DvLinnCoUkProduct1")]
        static extern unsafe void DvProviderLinnCoUkProduct1GetPropertyStandby(uint aHandle, int* aValue);
        [DllImport("DvLinnCoUkProduct1")]
        static extern void DvProviderLinnCoUkProduct1EnableActionRoom(uint aHandle, CallbackRoom aCallback, IntPtr aPtr);
        [DllImport("DvLinnCoUkProduct1")]
        static extern void DvProviderLinnCoUkProduct1EnableActionSetRoom(uint aHandle, CallbackSetRoom aCallback, IntPtr aPtr);
        [DllImport("DvLinnCoUkProduct1")]
        static extern void DvProviderLinnCoUkProduct1EnableActionStandby(uint aHandle, CallbackStandby aCallback, IntPtr aPtr);
        [DllImport("DvLinnCoUkProduct1")]
        static extern void DvProviderLinnCoUkProduct1EnableActionSetStandby(uint aHandle, CallbackSetStandby aCallback, IntPtr aPtr);
        [DllImport("ZappUpnp")]
        static extern unsafe void ZappFree(void* aPtr);

        private unsafe delegate int CallbackRoom(IntPtr aPtr, uint aVersion, char** aaRoom);
        private unsafe delegate int CallbackSetRoom(IntPtr aPtr, uint aVersion, char* aaRoom);
        private unsafe delegate int CallbackStandby(IntPtr aPtr, uint aVersion, int* aaStandby);
        private unsafe delegate int CallbackSetStandby(IntPtr aPtr, uint aVersion, int aaStandby);

        private GCHandle iGch;
        private CallbackRoom iCallbackRoom;
        private CallbackSetRoom iCallbackSetRoom;
        private CallbackStandby iCallbackStandby;
        private CallbackSetStandby iCallbackSetStandby;

        public DvProviderLinnCoUkProduct1(DvDevice aDevice)
        {
            iHandle = DvProviderLinnCoUkProduct1Create(aDevice.Handle()); 
            iGch = GCHandle.Alloc(this);
        }

        public unsafe bool SetPropertyRoom(string aValue)
        {
        uint changed;
            char* value = (char*)Marshal.StringToHGlobalAnsi(aValue).ToPointer();
            int err = DvProviderLinnCoUkProduct1SetPropertyRoom(iHandle, value, &changed);
            Marshal.FreeHGlobal((IntPtr)value);
            if (err != 0)
            {
                throw(new PropertyUpdateError());
            }
            return (changed != 0);
        }

        public unsafe void GetPropertyRoom(out string aValue)
        {
            char* value;
            DvProviderLinnCoUkProduct1GetPropertyRoom(iHandle, &value);
            aValue = Marshal.PtrToStringAnsi((IntPtr)value);
            ZappFree(value);
        }

        public unsafe bool SetPropertyStandby(bool aValue)
        {
        uint changed;
            int value = (aValue ? 1 : 0);
            if (0 != DvProviderLinnCoUkProduct1SetPropertyStandby(iHandle, value, &changed))
            {
                throw(new PropertyUpdateError());
            }
            return (changed != 0);
        }

        public unsafe void GetPropertyStandby(out bool aValue)
        {
            int value;
            DvProviderLinnCoUkProduct1GetPropertyStandby(iHandle, &value);
            aValue = (value != 0);
        }

        protected unsafe void EnableActionRoom()
        {
            iCallbackRoom = new CallbackRoom(DoRoom);
            IntPtr ptr = GCHandle.ToIntPtr(iGch);
            DvProviderLinnCoUkProduct1EnableActionRoom(iHandle, iCallbackRoom, ptr);
        }

        protected unsafe void EnableActionSetRoom()
        {
            iCallbackSetRoom = new CallbackSetRoom(DoSetRoom);
            IntPtr ptr = GCHandle.ToIntPtr(iGch);
            DvProviderLinnCoUkProduct1EnableActionSetRoom(iHandle, iCallbackSetRoom, ptr);
        }

        protected unsafe void EnableActionStandby()
        {
            iCallbackStandby = new CallbackStandby(DoStandby);
            IntPtr ptr = GCHandle.ToIntPtr(iGch);
            DvProviderLinnCoUkProduct1EnableActionStandby(iHandle, iCallbackStandby, ptr);
        }

        protected unsafe void EnableActionSetStandby()
        {
            iCallbackSetStandby = new CallbackSetStandby(DoSetStandby);
            IntPtr ptr = GCHandle.ToIntPtr(iGch);
            DvProviderLinnCoUkProduct1EnableActionSetStandby(iHandle, iCallbackSetStandby, ptr);
        }

        protected virtual void Room(uint aVersion, out string aaRoom)
        {
            throw (new ActionDisabledError());
        }

        protected virtual void SetRoom(uint aVersion, string aaRoom)
        {
            throw (new ActionDisabledError());
        }

        protected virtual void Standby(uint aVersion, out bool aaStandby)
        {
            throw (new ActionDisabledError());
        }

        protected virtual void SetStandby(uint aVersion, bool aaStandby)
        {
            throw (new ActionDisabledError());
        }

        private static unsafe int DoRoom(IntPtr aPtr, uint aVersion, char** aaRoom)
        {
            GCHandle gch = GCHandle.FromIntPtr(aPtr);
            DvProviderLinnCoUkProduct1 self = (DvProviderLinnCoUkProduct1)gch.Target;
            string aRoom;
            self.Room(aVersion, out aRoom);
            *aaRoom = (char*)Marshal.StringToHGlobalAnsi(aRoom).ToPointer();
            return 0;
        }

        private static unsafe int DoSetRoom(IntPtr aPtr, uint aVersion, char* aaRoom)
        {
            GCHandle gch = GCHandle.FromIntPtr(aPtr);
            DvProviderLinnCoUkProduct1 self = (DvProviderLinnCoUkProduct1)gch.Target;
            string aRoom = Marshal.PtrToStringAnsi((IntPtr)aaRoom);
            self.SetRoom(aVersion, aRoom);
            return 0;
        }

        private static unsafe int DoStandby(IntPtr aPtr, uint aVersion, int* aaStandby)
        {
            GCHandle gch = GCHandle.FromIntPtr(aPtr);
            DvProviderLinnCoUkProduct1 self = (DvProviderLinnCoUkProduct1)gch.Target;
            bool aStandby;
            self.Standby(aVersion, out aStandby);
            *aaStandby = (aStandby ? 1 : 0);
            return 0;
        }

        private static unsafe int DoSetStandby(IntPtr aPtr, uint aVersion, int aaStandby)
        {
            GCHandle gch = GCHandle.FromIntPtr(aPtr);
            DvProviderLinnCoUkProduct1 self = (DvProviderLinnCoUkProduct1)gch.Target;
            bool aStandby = (aaStandby != 0);
            self.SetStandby(aVersion, aStandby);
            return 0;
        }


        public void Dispose()
        {
            DoDispose();
            GC.SuppressFinalize(this);
        }

        ~DvProviderLinnCoUkProduct1()
        {
            DoDispose();
        }

        private void DoDispose()
        {
            uint handle;
            lock (this)
            {
                if (iHandle == 0)
                {
                    return;
                }
                handle = iHandle;
                iHandle = 0;
            }
            DvProviderLinnCoUkProduct1Destroy(handle);
            if (iGch.IsAllocated)
            {
                iGch.Free();
            }
        }
    }
}

