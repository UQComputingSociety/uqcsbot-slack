module Main (setup) where

import Scripts (Script, scripts)
import Data.Foldable (traverse_)


setup :: Script
setup r = traverse_ (\x -> x r) scripts
