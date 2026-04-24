import { Tabs } from "expo-router";
import Ionicons from '@expo/vector-icons/Ionicons';
import { Slot } from "expo-router";
import { Link, useRouter, Redirect } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';
export default function RootLayout() {
  let hello = 1;
  const getData = async () => {
    try {
      const value = await AsyncStorage.getItem('sessionID');
      console.log(value); 
      if (value !== null) {hello = 0;}
      else{
        hello = 1;
      } 
    }
    catch(e){
        console.log('error');
        }

}	
      
     const returnstate = getData().then(() => {
      if (hello == 1) {
      return <Redirect href="/login" />;
      }
  console.log('fuck');    
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
  });
  return returnstate;
}
  