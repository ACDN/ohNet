#ifndef HEADER_DVLINNCOUKDEBUG2_C
#define HEADER_DVLINNCOUKDEBUG2_C

#include <OsTypes.h>
#include <C/DvDevice.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef int32_t (*CallbackDebug2SetDebugLevel)(void* aPtr, uint32_t aVersion, uint32_t aaDebugLevel);
typedef int32_t (*CallbackDebug2DebugLevel)(void* aPtr, uint32_t aVersion, uint32_t* aaDebugLevel);
typedef int32_t (*CallbackDebug2MemWrite)(void* aPtr, uint32_t aVersion, uint32_t aaMemAddress, const char* aaMemData, uint32_t aaMemDataLen);

DllExport THandle DvProviderLinnCoUkDebug2Create(DvDeviceC aDevice);
DllExport void DvProviderLinnCoUkDebug2Destroy(THandle aProvider);

DllExport void DvProviderLinnCoUkDebug2EnableActionSetDebugLevel(THandle aProvider, CallbackDebug2SetDebugLevel aCallback, void* aPtr);
DllExport void DvProviderLinnCoUkDebug2EnableActionDebugLevel(THandle aProvider, CallbackDebug2DebugLevel aCallback, void* aPtr);
DllExport void DvProviderLinnCoUkDebug2EnableActionMemWrite(THandle aProvider, CallbackDebug2MemWrite aCallback, void* aPtr);


#ifdef __cplusplus
} // extern "C"
#endif

#endif // HEADER_DVLINNCOUKDEBUG2_C

