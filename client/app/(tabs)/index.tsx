import { Text, View, StyleSheet } from "react-native";
import { SafeAreaView } from 'react-native-safe-area-context';
import { Link } from 'expo-router';
import Button from '@/components/Button';
import Input from '@/components/Input';
export default function Index() {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.poster}>
	<Input/>
      </View>
      <View style={styles.space}/>
      <View style={styles.link}>
      <Link href="/about" style={styles.button}>
        Go to About Screen
      </Link>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#00000f',
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    color: '#eee',
  },
  button: {
    fontSize: 15,
    textDecorationLine: 'underLine',
    color: '#ccc',
  },
  poster: {
    flex: 1,
    height: '100%',
    width: '100%',
    justifyContent:'center',
    alignItems: 'center',
  },
  link: {
    justifyContent: 'flex-end',
    },
  space: {
    flex: 1/3,
    },
    
});