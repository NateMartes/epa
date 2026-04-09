import { Tabs } from "expo-router";
import Ionicons from '@expo/vector-icons/Ionicons';
import { Slot } from "expo-router";
import { Link, useRouter } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
export default function RootLayout() {
  const router = useRouter();
  const getData = async () => {
    try {
      const value = await AsyncStorage.getItem('sessionID');
      console.log(value);
      if(value == null){
      router.navigate('/login'); }
      if (value !== null) {
      }
      else{
        return null;
      }
    }
  catch(e){
        console.log('error');
        }
  }
  const hello = getData();
  
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#ff0033',
        headerStyle: {
          backgroundColor: '#25292e',
        },
        headerShadowVisible: false,
        headerTintColor: '#fff',
        tabBarStyle: {
          backgroundColor: '#25292e',
          },
        }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          tabBarIcon: ({ color, focused }) => (
            <Ionicons name={focused ? 'home-sharp' : 'home-outline'} color={color} size={30} />
          ),
        }}
      />
      <Tabs.Screen
        name="about"
        options={{
          title: 'About',
          tabBarIcon: ({ color, focused }) => (
            <Ionicons name={focused ? 'information-circle' : 'information-circle-outline'} color={color} size={30} />
          ),
        }}
      />
    </Tabs>
  );
}
  