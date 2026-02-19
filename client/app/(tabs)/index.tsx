import { Text, View, StyleSheet } from "react-native";
import { SafeAreaView } from 'react-native-safe-area-context';
import { Link } from 'expo-router';
import Button from '@/components/Button';

export default function Index() {
  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.footerContainer}>
        <Button theme="primary" label="Make Post" />
      </View>
      <Text style={styles.text}>Home screen</Text>
      <Link href="/about" style={styles.button}>
        Go to About Screen
      </Link>
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
    fontSize: 25,
    textDecorationLine: 'underLine',
    color: '#fff',
  },
  footerContainer: {
    flex: 1 / 3,
    alignItems: 'center',
  },
});