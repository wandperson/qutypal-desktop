# Basic
import platform
import ctypes
from ctypes.util import find_library
from abc import ABC, abstractmethod



class PlatformProvider(ABC):
    @abstractmethod
    def get_idle_time(self):
        pass

    @abstractmethod
    def is_fullscreen(self):
        pass



class LinuxPlatform(PlatformProvider):
    def get_idle_time(self):
        # Load the X11 and XScreenSaver libraries
        x11_path = find_library("X11")
        if not x11_path:
            raise RuntimeError("libX11 not found")
        xlib = ctypes.cdll.LoadLibrary(x11_path)

        xss_path = find_library("Xss")
        if not xss_path:
            raise RuntimeError("libXss not found")
        xss = ctypes.cdll.LoadLibrary(xss_path)

        # xlib = ctypes.cdll.LoadLibrary("libX11.so")
        # self.xss = ctypes.cdll.LoadLibrary("libXss.so")

        # Open display
        self.display = xlib.XOpenDisplay(None)
        if not self.display:
            raise Exception("Cannot open display")
        
        class XScreenSaverInfo(ctypes.Structure):
            _fields_ = [("window", ctypes.c_ulong),
                        ("state", ctypes.c_int),
                        ("kind", ctypes.c_int),
                        ("since", ctypes.c_ulong),
                        ("idle", ctypes.c_ulong),
                        ("event_mask", ctypes.c_ulong)]

        # Create a pointer for XScreenSaverInfo
        xss_info = XScreenSaverInfo()
        xss.XScreenSaverAllocInfo.restype = ctypes.POINTER(XScreenSaverInfo)
        xss_info_ptr = xss.XScreenSaverAllocInfo()

        # Get idle time
        xss.XScreenSaverQueryInfo(self.display, xlib.XDefaultRootWindow(self.display), xss_info_ptr)
        idle_time = xss_info_ptr.contents.idle / 1000  # Idle time is in milliseconds
        return idle_time

    def is_fullscreen(self):
        from Xlib import display, X
        import Xlib.error

        d = display.Display()
        root = d.screen().root
        NET_ACTIVE_WINDOW = d.intern_atom('_NET_ACTIVE_WINDOW')
        NET_WM_STATE = d.intern_atom('_NET_WM_STATE')
        NET_WM_STATE_FULLSCREEN = d.intern_atom('_NET_WM_STATE_FULLSCREEN')
        try:
            window_id = root.get_full_property(NET_ACTIVE_WINDOW, X.AnyPropertyType).value[0]
            window = d.create_resource_object('window', window_id)
            wm_state = window.get_full_property(NET_WM_STATE, X.AnyPropertyType)
            if wm_state and NET_WM_STATE_FULLSCREEN in wm_state.value:
                return True
        except Xlib.error.XError:
            pass
        return False



class WindowsPlatform(PlatformProvider):
    def get_idle_time(self):
        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint),
                        ("dwTime", ctypes.c_uint)]

        lii = LASTINPUTINFO()
        lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))

        millis_since_system_start = ctypes.windll.kernel32.GetTickCount()
        idle_time = (millis_since_system_start - lii.dwTime) / 1000.0
        return idle_time

    def is_fullscreen(self):
        # Missed implementation of is
        # window in OS is fullscreen
        return False



class PlatformManager(PlatformProvider):
    def __init__(self):
        providers = {
            'Linux': LinuxPlatform(),
            'Windows': WindowsPlatform()
        }

        os_type = platform.system()
        provider = providers.get(os_type)
        
        if provider:
            self.provider = provider
        else:
            raise NotImplementedError(f"Unsupported platform: {os_type}")

    # It's better, but IDE don't see methods to autocomplete
    # def __getattr__(self, name):
    #     return getattr(self.provider, name)
    
    def get_idle_time(self):
        return self.provider.get_idle_time()

    def is_fullscreen(self):
        return self.provider.is_fullscreen()



platman = PlatformManager()